import { useQuery, useMutation, useQueryClient } from 'react-query'
import { economyApi, marketApi, authApi } from '@/lib/api'
import { getStoredUserId } from '@/utils'
import { notifySuccess, notifyError } from '@/lib/notifications'
import { useMemo } from 'react'
import type { Auction } from '@/types'

export function useWallet() {
  const userId = useMemo(() => getStoredUserId(), [])

  const {
    data: wallet,
    isLoading,
    error,
  } = useQuery(['wallet', userId], () => economyApi.getWallet(userId), {
    refetchInterval: 10000, // чаще, чтобы видеть награды за стадии быстрее
    retry: 2,
    staleTime: 5000, // данные считаются свежими 5 секунд
    cacheTime: 300000, // Cache for 5 минут
  })

  return {
    wallet,
    isLoading,
    error,
  }
}

export function useTransactions(limit: number = 20) {
  const userId = useMemo(() => getStoredUserId(), [])

  const {
    data: transactionsData,
    isLoading,
    error,
  } = useQuery(['transactions', userId, limit], () => economyApi.getTransactions(userId, limit), {
    refetchInterval: 60000, // Refetch every minute
    retry: 2,
  })

  return {
    transactions: transactionsData?.transactions || [],
    total: transactionsData?.total || 0,
    isLoading,
    error,
  }
}

export function useUserStats() {
  const userId = useMemo(() => getStoredUserId(), [])

  const {
    data: stats,
    isLoading,
    error,
  } = useQuery(['userStats', userId], () => economyApi.getUserStats(userId), {
    refetchInterval: 60000, // Refetch every minute
    retry: 2,
  })

  return {
    stats,
    isLoading,
    error,
  }
}

export function useActionCosts() {
  const {
    data: actionCosts,
    isLoading,
    error,
  } = useQuery(['actionCosts'], () => economyApi.getActionCosts(), {
    refetchInterval: 300000, // Refetch every 5 minutes
    retry: 2,
  })

  return {
    actionCosts,
    isLoading,
    error,
  }
}

export function useDailyLogin() {
  const queryClient = useQueryClient()
  const userId = useMemo(() => getStoredUserId(), [])

  const dailyLoginMutation = useMutation(
    () => economyApi.claimDailyLogin(userId),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['wallet', userId])
        notifySuccess(`Получено ${data.reward_amount} монет!`)
      },
      onError: (error: any) => {
        notifyError(error.response?.data?.detail || 'Ошибка получения награды')
      },
    }
  )

  return {
    claimDailyLogin: dailyLoginMutation.mutate,
    isClaiming: dailyLoginMutation.isLoading,
  }
}

export function usePurchaseCoins() {
  const queryClient = useQueryClient()
  const userId = useMemo(() => getStoredUserId(), [])

  const purchaseMutation = useMutation(
    ({ packageId }: { packageId: string }) => economyApi.purchaseCoins(userId, packageId),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['wallet', userId])
        notifySuccess(`Куплено ${data.coins_added} монет!`)
      },
      onError: (error: any) => {
        notifyError(error.response?.data?.detail || 'Ошибка покупки монет')
      },
    }
  )

  return {
    purchaseCoins: purchaseMutation.mutate,
    isPurchasing: purchaseMutation.isLoading,
  }
} 

// Баланс монет с умной резолюцией источника
// Приоритет: явное значение -> live кошелёк (useWallet) -> кэш allPets -> неизвестно
export function useCoinBalance(explicitCoins?: number) {
  const queryClient = useQueryClient()
  const userId = useMemo(() => getStoredUserId(), [])

  // 1) Явное значение имеет приоритет
  const explicit = typeof explicitCoins === 'number' ? explicitCoins : undefined

  // 2) Live-кошелёк из /economy кошелька
  const { wallet } = useWallet()
  const liveCoins = typeof wallet?.coins === 'number' ? wallet!.coins : undefined

  // 3) Фолбэк: кэш из ['allPets', userId]
  const allPetsData: any = queryClient.getQueryData(['allPets', userId])
  const cachedCoins = typeof allPetsData?.wallet?.coins === 'number' ? allPetsData.wallet.coins : undefined

  const coins = explicit ?? liveCoins ?? cachedCoins

  const canAfford = (cost: number) => {
    if (typeof cost !== 'number' || Number.isNaN(cost)) return true
    if (typeof coins !== 'number') return true // неизвестно — не блокируем кнопку
    return coins >= cost
  }

  return { coins, canAfford }
}

// ====== РЫНОК / АУКЦИОНЫ ======

export function useAuctions(status: string = 'active', page: number = 1, pageSize: number = 20) {
  const { data, isLoading, error, refetch } = useQuery(['auctions', status, page, pageSize], () => marketApi.listAuctions({ status, page, page_size: pageSize }), {
    refetchInterval: 5000,
  })
  return { auctions: (data?.items || []) as Auction[], page: data?.page || page, pageSize: data?.page_size || pageSize, isLoading, error, refetch }
}

export function usePlaceBid() {
  const queryClient = useQueryClient()
  const userId = useMemo(() => getStoredUserId(), [])
  const mutation = useMutation(
    async ({ auctionId, amount }: { auctionId: number; amount: number }) => {
      let token = localStorage.getItem('auth_token')
      if (!token) {
        const username = localStorage.getItem('username')
        const res = await authApi.issueToken(userId, username)
        token = res.access_token
        localStorage.setItem('auth_token', token)
      }
      return marketApi.placeBid({ auction_id: auctionId, amount })
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('auctions')
        notifySuccess('Ставка принята')
      },
      onError: (error: any) => {
        notifyError(error.response?.data?.detail || 'Ошибка ставки')
      },
    }
  )
  return { placeBid: mutation.mutate, isPlacing: mutation.isLoading }
}

export function useCreateAuction() {
  const queryClient = useQueryClient()
  const userId = useMemo(() => getStoredUserId(), [])
  const mutation = useMutation(
    async ({ petId, startPrice, durationSeconds, buyNowPrice }: { petId: number; startPrice: number; durationSeconds?: number; buyNowPrice?: number }) => {
      let token = localStorage.getItem('auth_token')
      if (!token) {
        const username = localStorage.getItem('username')
        const res = await authApi.issueToken(userId, username)
        token = res.access_token
        localStorage.setItem('auth_token', token)
      }
      return marketApi.createAuction({ pet_id: petId, start_price: startPrice, duration_seconds: durationSeconds, buy_now_price: buyNowPrice } as any)
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('auctions')
        notifySuccess('Аукцион создан')
      },
      onError: (error: any) => {
        notifyError(error.response?.data?.detail || 'Ошибка создания аукциона')
      },
    }
  )
  return { createAuction: mutation.mutate, isCreating: mutation.isLoading }
}

export function useBuyNow() {
  const queryClient = useQueryClient()
  const userId = useMemo(() => getStoredUserId(), [])
  const mutation = useMutation(
    async ({ auctionId }: { auctionId: number }) => {
      let token = localStorage.getItem('auth_token')
      if (!token) {
        const username = localStorage.getItem('username')
        const res = await authApi.issueToken(userId, username)
        token = res.access_token
        localStorage.setItem('auth_token', token)
      }
      return marketApi.buyNow({ auction_id: auctionId })
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('auctions')
        notifySuccess('Покупка выполнена')
      },
      onError: (error: any) => {
        notifyError(error.response?.data?.detail || 'Ошибка покупки')
      },
    }
  )
  return { buyNow: mutation.mutate, isBuying: mutation.isLoading }
}