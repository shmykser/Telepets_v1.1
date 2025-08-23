import axios from 'axios'
import type { 
  Pet, 
  Wallet, 
  Transaction, 
  UserStats, 
  ActionCosts, 
  PetSummary,
  HealthUpResponse,
  CreatePetResponse,
  ApiError,
  Auction,
  AuctionBid,
  UserProfile,
  UpdateProfileRequest,
  PublicUserInfo
} from '@/types'

// В dev принудительно используем прокси Vite, чтобы не ловить CORS
const API_BASE_URL = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || '/api')

// Базовый клиент для всех запросов
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Отдельный клиент без интерсепторов для /auth/token, чтобы избежать рекурсии
const authClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

const AUTH_TOKEN_PATH = '/auth/token'
let isIssuingToken = false

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    // Пропускаем авторизацию для запроса получения токена
    if ((config.url || '').includes(AUTH_TOKEN_PATH)) {
      return config
    }

    // Add auth token if available
    let token = localStorage.getItem('auth_token')

    // Если токена нет, пробуем получить его один раз без рекурсии
    if (!token && !isIssuingToken) {
      try {
        isIssuingToken = true
        const userId = localStorage.getItem('user_id') || 'default_user'
        const username = localStorage.getItem('username') || undefined
        const params: any = { user_id: userId }
        if (username) params.username = username
        const resp = await authClient.post(AUTH_TOKEN_PATH, null, { params })
        token = resp.data?.access_token
        if (token) {
          localStorage.setItem('auth_token', token)
        }
      } catch (error) {
        console.warn('Не удалось автоматически получить токен:', error)
      } finally {
        isIssuingToken = false
      }
    }

    if (token) {
      (config.headers = config.headers || {}).Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
    }
    return Promise.reject(error)
  }
)

// Pet API
export const petApi = {
  // Create a new pet
  createPet: async (user_id: string, name: string, override: boolean = false): Promise<CreatePetResponse> => {
    const response = await api.post<CreatePetResponse>('/create', null, {
      params: { user_id, name, override: override ? 'true' : 'false' },
      // Создание питомца может занимать заметное время — увеличим таймаут для запроса
      timeout: 60000,
    })
    return response.data
  },

  // Get pet summary
  getSummary: async (user_id: string): Promise<Pet> => {
    const response = await api.get<Pet>('/summary', {
      params: { user_id }
    })
    return response.data
  },

  // Get all pets
  getAllPets: async (user_id: string): Promise<PetSummary> => {
    const response = await api.get<PetSummary>('/summary/all', {
      params: { user_id }
    })
    return response.data
  },

  // Select active pet by name (server-side support to be added if needed)
  // For now, fetch all and filter on client

  // Increase pet health (optionally by pet name)
  healthUp: async (user_id: string, pet_name?: string): Promise<HealthUpResponse> => {
    const response = await api.post<HealthUpResponse>('/health_up', null, {
      params: { user_id, pet_name }
    })
    return response.data
  },

  // Increase pet health with cost
  healthUpWithCost: async (user_id: string, pet_name?: string): Promise<HealthUpResponse> => {
    const response = await api.post<any>(`/economy/actions/${encodeURIComponent(user_id)}/health_up`, null, {
      params: { pet_name }
    })
    // Бэкенд возвращает обёртку { success, coins_spent, new_balance, pet_info }
    // Возвращаем только pet_info, чтобы интерфейс совпадал с HealthUpResponse
    return response.data?.pet_info as HealthUpResponse
  },
}

// Economy API
export const economyApi = {
  // Get wallet
  getWallet: async (user_id: string): Promise<Wallet> => {
    const response = await api.get<Wallet>(`/economy/wallet/${user_id}`)
    return response.data
  },

  // Get balance
  getBalance: async (user_id: string): Promise<{ user_id: string; coins: number }> => {
    const response = await api.get<{ user_id: string; coins: number }>(`/economy/balance/${user_id}`)
    return response.data
  },

  // Get transactions
  getTransactions: async (user_id: string, limit: number = 20): Promise<{ user_id: string; transactions: Transaction[]; total: number }> => {
    const response = await api.get<{ user_id: string; transactions: Transaction[]; total: number }>(`/economy/transactions/${user_id}`, {
      params: { limit }
    })
    return response.data
  },

  // Get user stats
  getUserStats: async (user_id: string): Promise<UserStats> => {
    const response = await api.get<UserStats>(`/economy/stats/${user_id}`)
    return response.data
  },

  // Purchase coins
  purchaseCoins: async (user_id: string, package_id: string): Promise<{
    success: boolean
    user_id: string
    coins_added: number
    price_usd: number
    package_id: string
  }> => {
    const response = await api.post<{
      success: boolean
      user_id: string
      coins_added: number
      price_usd: number
      package_id: string
    }>(`/economy/purchase/${user_id}`, null, {
      params: { package_id }
    })
    return response.data
  },

  // Get action costs
  getActionCosts: async (): Promise<ActionCosts> => {
    const response = await api.get<ActionCosts>('/economy/actions/costs')
    return response.data
  },

  // Claim daily login reward
  claimDailyLogin: async (user_id: string): Promise<{
    success: boolean
    reward_amount: number
    new_balance: number
    message: string
  }> => {
    const response = await api.post<{
      success: boolean
      user_id: string
      reward_amount: number
      new_balance: number
      message: string
    }>(`/economy/rewards/${user_id}/daily_login`)
    return response.data
  },

  // Resurrect pet
  resurrectPet: async (user_id: string, pet_name: string): Promise<{
    success: boolean
    coins_spent: number
    new_balance: number
    pet: { id: number; name: string; state: string; health: number; status: string }
  }> => {
    const response = await api.post(`/economy/actions/${encodeURIComponent(user_id)}/resurrect`, null, {
      params: { pet_name }
    })
    return response.data
  },

  // Claim game reward
  claimGameReward: async (user_id: string, game: string, score: number): Promise<{
    success: boolean
    coins_added: number
    new_balance: number
    message: string
  }> => {
    const response = await api.post(`/economy/games/${encodeURIComponent(user_id)}/claim`, null, {
      params: { game, score }
    })
    return response.data
  },
}

// Monitoring API
export const monitoringApi = {
  // Health check
  getHealth: async (): Promise<any> => {
    const response = await api.get('/monitoring/health')
    return response.data
  },

  // Get metrics
  getMetrics: async (): Promise<any> => {
    const response = await api.get('/monitoring/metrics')
    return response.data
  },

  // Get statistics
  getStats: async (): Promise<any> => {
    const response = await api.get('/monitoring/stats')
    return response.data
  },

  // Get user history
  getUserHistory: async (user_id: string): Promise<any> => {
    const response = await api.get(`/monitoring/users/${user_id}/history`)
    return response.data
  },
}

// Market API
export const marketApi = {
  listAuctions: async (params?: { status?: string; page?: number; page_size?: number }): Promise<{ items: Auction[]; page: number; page_size: number }> => {
    const response = await api.get('/market/auctions', { params })
    return response.data
  },

  getAuction: async (auctionId: number): Promise<Auction> => {
    const response = await api.get(`/market/auctions/${auctionId}`)
    return response.data
  },

  createAuction: async (payload: {
    pet_id: number
    start_price: number
    duration_seconds?: number
    buy_now_price?: number
    min_increment_abs?: number
    min_increment_pct?: number
  }): Promise<{ id: number; end_time: string; status: string }> => {
    const { user_id, ...params } = (payload as any)
    const response = await api.post('/market/auctions', null, { params })
    return response.data
  },

  placeBid: async (payload: { auction_id: number; amount: number }): Promise<{ auction: Auction; bid: AuctionBid }> => {
    const response = await api.post(`/market/auctions/${payload.auction_id}/bids`, null, { params: { amount: payload.amount } })
    return response.data
  },

  buyNow: async (payload: { auction_id: number }): Promise<{ id: number; status: string }> => {
    const response = await api.post(`/market/auctions/${payload.auction_id}/buy_now`)
    return response.data
  },

  cancel: async (payload: { auction_id: number }): Promise<{ id: number; status: string }> => {
    const response = await api.post(`/market/auctions/${payload.auction_id}/cancel`)
    return response.data
  },
}

// Auth API (MVP): авто-выдача токена по user_id — используем authClient без интерсепторов
export const authApi = {
  issueToken: async (user_id: string, username?: string): Promise<{ access_token: string; token_type: string; user_id: string }> => {
    const params: any = { user_id }
    if (username) {
      params.username = username
    }
    const response = await authClient.post(AUTH_TOKEN_PATH, null, { params })
    return response.data
  },
}

// User Profile API
export const userProfileApi = {
  // Получить профиль текущего пользователя
  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get<UserProfile>('/users/profile')
    return response.data
  },

  // Обновить настройки профиля
  updateProfile: async (data: UpdateProfileRequest): Promise<UserProfile> => {
    const response = await api.put<UserProfile>('/users/profile', data)
    return response.data
  },

  // Получить публичную информацию о пользователе
  getPublicInfo: async (userId: string): Promise<PublicUserInfo> => {
    const response = await api.get<PublicUserInfo>(`/users/${userId}/public`)
    return response.data
  },
}

export default api 