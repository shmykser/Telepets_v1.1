import { useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { getStoredUserId, formatTime } from '@/utils'
import { useBuyNow, usePlaceBid } from '@/hooks/useEconomy'
import useTimer from '@/hooks/useTimer'
import type { Auction } from '@/types'
import { useQuery } from 'react-query'
import { petApi } from '@/lib/api'
import { Coins, User } from 'lucide-react'

export default function AuctionCard({ auction, onAction }: { auction: Auction; onAction?: () => void }) {
  const userId = useMemo(() => getStoredUserId(), [])
  const [bid, setBid] = useState<number>(auction.current_price + 1)
  const secondsLeft = useMemo(() => {
    const raw = auction.end_time as unknown as string
    // Если в ISO строке нет таймзоны, трактуем как UTC (добавляем 'Z')
    const hasTz = /Z|[+-]\d{2}:?\d{2}$/.test(raw)
    const end = new Date(hasTz ? raw : `${raw}Z`).getTime()
    const now = Date.now()
    return Math.max(0, Math.floor((end - now) / 1000))
  }, [auction.end_time])
  const timer = useTimer(secondsLeft, { autoplay: true, pauseWhenHidden: true })

  const { placeBid, isPlacing } = usePlaceBid()
  const { buyNow, isBuying } = useBuyNow()

  const handleBid = () => {
    if (youAreLeader || isOwner) return
    placeBid({ auctionId: auction.id, amount: bid })
    onAction?.()
  }

  const handleBuyNow = () => {
    buyNow({ auctionId: auction.id })
    onAction?.()
  }

  const youAreLeader = auction.current_winner_user_id === userId
  const isOwner = auction.seller_user_id === userId

  // Подтягиваем имя питомца продавца, чтобы построить URL изображения
  const { data: sellerPetsData } = useQuery(
    ['sellerPets', auction.seller_user_id],
    () => petApi.getAllPets(auction.seller_user_id),
    { staleTime: 10000, retry: 1 }
  )
  const sellerPet = useMemo(() => {
    const list = (sellerPetsData as any)?.pets || []
    return list.find((p: any) => p.id === auction.pet_id)
  }, [sellerPetsData, auction.pet_id])
  // Абсолютный URL для изображений на домен API, чтобы не ловить 404/CORS на фронтовом домене
  const apiBase = (import.meta as any).env?.VITE_API_URL || ''
  const imageUrl = sellerPet?.name
    ? `${apiBase.replace(/\/$/, '')}/pet-images/${auction.seller_user_id}/${encodeURIComponent(sellerPet.name)}`
    : undefined

  return (
    <Card>
      <CardHeader>
        <CardTitle>Лот #{auction.id}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="w-full aspect-video rounded-lg overflow-hidden border border-border bg-slate-900/40">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={sellerPet?.name || 'pet'}
              className="w-full h-full object-cover"
              onError={(e) => {
                const el = e.target as HTMLImageElement
                el.style.display = 'none'
                const fb = el.parentElement?.querySelector('.fallback') as HTMLElement
                if (fb) fb.style.display = 'flex'
              }}
            />
          ) : null}
          <div className="fallback hidden absolute inset-0 items-center justify-center text-slate-500 text-sm">
            Изображение недоступно
          </div>
        </div>
        <div className="text-sm text-slate-400">Питомец ID: {auction.pet_id}</div>
        {auction.seller_name && (
          <div className="text-sm text-slate-400 flex items-center space-x-2">
            <User size={14} />
            <span>Продавец: {auction.seller_name}</span>
          </div>
        )}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-slate-400 text-sm">Текущая цена</div>
            <div className="text-xl font-semibold flex items-center space-x-2">
              <Coins size={18} className="text-yellow-400" />
              <span>{auction.current_price}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-slate-400 text-sm">Осталось</div>
            <div className="text-xl font-semibold">{formatTime(timer.secondsLeft)}</div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="number"
            className="flex-1 rounded-md bg-surface border border-border px-3 py-2 text-sm"
            value={bid}
            min={auction.current_price + 1}
            onChange={(e) => setBid(parseInt(e.target.value, 10))}
            disabled={youAreLeader || isOwner}
          />
          <Button onClick={handleBid} disabled={isPlacing || youAreLeader || isOwner}>Ставка</Button>
        </div>
        {auction.buy_now_price != null && (
          <Button variant="secondary" onClick={handleBuyNow} disabled={isBuying} className="flex items-center space-x-2">
            <Coins size={16} className="text-yellow-400" />
            <span>Купить сейчас за {auction.buy_now_price}</span>
          </Button>
        )}
        {youAreLeader && (
          <div className="text-green-400 text-sm">Вы лидер по ставке</div>
        )}
        {isOwner && (
          <div className="text-slate-400 text-xs">Это ваш лот</div>
        )}
      </CardContent>
    </Card>
  )
}


