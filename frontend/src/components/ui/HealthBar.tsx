import { cn, getHealthColor } from '@/lib/utils'

interface HealthBarProps {
  value: number
  className?: string
}

export default function HealthBar({ value, className }: HealthBarProps) {
  const colorClass = getHealthColor(value)
  const width = Math.max(0, Math.min(100, Math.round(value)))
  return (
    <div className={cn('health-bar', className)}>
      <div className={cn('health-fill', colorClass)} style={{ width: `${width}%` }} />
    </div>
  )
}


