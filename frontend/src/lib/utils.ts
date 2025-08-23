import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTime(seconds: number): string {
  if (seconds <= 0) return '00:00'
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Константы здоровья (должны соответствовать настройкам бэкенда)
const HEALTH_MAX = 100
const HEALTH_HIGH = 80
const HEALTH_MEDIUM = 50
const HEALTH_LOW = 20
const HEALTH_MIN = 0

export function getHealthColor(health: number): string {
  if (health >= HEALTH_HIGH) return 'health-high'
  if (health >= HEALTH_MEDIUM) return 'health-medium'
  if (health >= HEALTH_LOW) return 'health-low'
  return 'health-critical'
}

export function getHealthText(health: number): string {
  if (health >= HEALTH_HIGH) return 'Отличное'
  if (health >= HEALTH_MEDIUM) return 'Хорошее'
  if (health >= HEALTH_LOW) return 'Плохое'
  return 'Критическое'
}

// Константы стадий (должны соответствовать настройкам бэкенда)
const STAGE_TRANSITION_INTERVAL = 600 // 10 минут в секундах

export function getStageInfo(stage: string) {
  const stages = {
    egg: {
      name: 'Яйцо',
      emoji: '🥚',
      description: 'Требует тепло',
      color: 'pet-stage-egg',
      duration: STAGE_TRANSITION_INTERVAL,
    },
    baby: {
      name: 'Детеныш',
      emoji: '👶',
      description: 'Требует еду',
      color: 'pet-stage-baby',
      duration: STAGE_TRANSITION_INTERVAL,
    },
    teen: {
      name: 'Подросток',
      emoji: '🧒',
      description: 'Требует отдых',
      color: 'pet-stage-teen',
      duration: STAGE_TRANSITION_INTERVAL,
    },
    adult: {
      name: 'Взрослый',
      emoji: '👨',
      description: 'Требует внимание',
      color: 'pet-stage-adult',
      duration: 0, // Final stage
    },
    dead: {
      name: 'Мертвый',
      emoji: '💀',
      description: 'Питомец умер',
      color: 'pet-stage-dead',
      duration: 0,
    },
  }
  
  return stages[stage as keyof typeof stages] || stages.egg
}

// Константы стоимости действий (должны соответствовать настройкам бэкенда)
const ACTION_COSTS = {
  egg: 5,
  baby: 10,
  teen: 15,
  adult: 20,
}

export function getActionCost(stage: string): number {
  return ACTION_COSTS[stage as keyof typeof ACTION_COSTS] || 10
}

export function getActionMessage(stage: string): string {
  const messages = {
    egg: 'Согреть яйцо',
    baby: 'Покормить детеныша',
    teen: 'Дать отдохнуть подростку',
    adult: 'Порадовать взрослого',
  }
  
  return messages[stage as keyof typeof messages] || 'Помочь питомцу'
}

export function getRandomUserId(): string {
  return `user_${Math.random().toString(36).substr(2, 9)}`
}

export function getStoredUserId(): string {
  // Сначала проверяем localStorage
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId) {
    return storedUserId
  }
  
  // Затем проверяем TEST_USER_ID из .env
  const testUserId = import.meta.env.VITE_TEST_USER_ID
  if (testUserId) {
    return testUserId
  }
  
  // Если ничего нет, генерируем случайный ID
  return getRandomUserId()
}

export function setStoredUserId(userId: string): void {
  localStorage.setItem('user_id', userId)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
} 