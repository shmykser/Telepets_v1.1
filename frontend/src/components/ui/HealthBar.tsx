import { cn, getHealthColor } from '@/utils'

interface HealthBarProps {
  value: number
  className?: string
}

export default function HealthBar({ value, className }: HealthBarProps) {
  const colorClass = getHealthColor(value)
  // Гарантируем минимальную видимую ширину при положительном значении
  const clamped = Math.max(0, Math.min(100, Math.round(value)))
  const width = clamped === 0 ? 0 : Math.max(clamped, 4)
  return (
    <div className={cn('health-bar', className)}>
      <div className={cn('health-fill', colorClass)} style={{ width: `${width}%` }} />
    </div>
  )
}


