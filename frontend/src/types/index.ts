export interface Pet {
  id?: number
  user_id: string
  name?: string
  state?: 'egg' | 'baby' | 'adult'
  health?: number
  status: 'alive' | 'dead' | 'no_pets' | 'all_dead' | 'success'
  next_stage?: string
  time_to_next_stage_seconds?: number
  image_url?: string
  created_at?: string
  updated_at?: string
  total_pets: number
  alive_pets?: number
  dead_pets?: number
  selected_pet_type?: 'alive' | 'dead'
  life_status?: 'alive' | 'dead'
  wallet?: Wallet
  message?: string
}

export interface Wallet {
  coins: number
  total_earned: number
  total_spent: number
  created_at?: string
  updated_at?: string
}

export interface Transaction {
  id: number
  type: 'purchase' | 'earning' | 'spending' | 'bonus' | 'refund' | 'market_purchase' | 'market_sale' | 'market_fee'
  amount: number
  balance_before: number
  balance_after: number
  description: string
  status: 'pending' | 'completed' | 'failed' | 'cancelled'
  created_at: string
  transaction_data?: any
}

export interface UserStats {
  total_pets: number
  alive_pets: number
  dead_pets: number
  total_transactions: number
  total_coins_earned: number
  total_coins_spent: number
  current_balance: number
}

export interface ActionCosts {
  action_costs: {
    health_up: {
      egg: number
      baby: number
      teen: number
      adult: number
    }
    special_food: number
    medicine: number
    toy: number
    grooming: number
  }
  purchase_options: {
    [key: string]: {
      coins: number
      price_usd: number
    }
  }
}

export interface PetSummary {
  user_id: string
  total_pets: number
  alive_pets: number
  dead_pets: number
  pets: Pet[]
  wallet?: Wallet
}

export interface HealthUpResponse {
  message: string
  health: number
  health_increased: number
  stage: string
  pet_id: number
}

export interface CreatePetResponse {
  id: number
  user_id: string
  name: string
  state: string
  health: number
  image_url: string
  wallet: Wallet
}

export interface ApiError {
  detail: string
  error_type?: string
  timestamp?: number
}

export interface UserProfile {
  user_id: string
  telegram_username?: string
  display_name?: string
  is_anonymous: boolean
  first_name?: string
  last_name?: string
  public_name: string
  created_at: string
  updated_at?: string
}

export interface UpdateProfileRequest {
  is_anonymous?: boolean
  display_name?: string
}

export interface PublicUserInfo {
  user_id: string
  public_name: string
  is_anonymous: boolean
}

export type PetStage = 'egg' | 'baby' | 'adult'
export type PetStatus = 'alive' | 'dead' | 'no_pets' | 'all_dead' | 'success'
export type TransactionType = 'purchase' | 'earning' | 'spending' | 'bonus' | 'refund'
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'cancelled' 
export type AuctionStatus = 'active' | 'completed' | 'cancelled' | 'expired'

export interface Auction {
  id: number
  pet_id: number
  seller_user_id: string
  seller_name: string  // Анонимное имя продавца
  start_price: number
  current_price: number
  buy_now_price?: number
  min_increment_abs?: number
  min_increment_pct?: number
  soft_close_seconds: number
  status: AuctionStatus
  current_winner_user_id?: string
  started_at: string
  end_time: string
  updated_at?: string
}

export interface AuctionBid {
  id: number
  auction_id: number
  bidder_user_id: string
  amount: number
  created_at: string
}