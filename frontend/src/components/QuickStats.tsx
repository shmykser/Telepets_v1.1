import { Card, CardContent } from '@/components/ui/Card'
import { Heart, Coins, Users, Skull } from 'lucide-react'
import { cn } from '@/utils'
import { Link } from 'react-router-dom'

export type QuickStatItem = 'totalPets' | 'alivePets' | 'deadPets' | 'coins' | 'status'

interface QuickStatsData {
  totalPets: number
  alivePets?: number
  deadPets?: number
  coins?: number
  statusText?: string
}

type Columns = 1 | 2 | 3 | 4
type Size = 'sm' | 'md' | 'lg'

interface QuickStatsProps {
  items?: QuickStatItem[]
  data: QuickStatsData
  columns?: Columns // фиксированное число колонок (без адаптивности)
  size?: Size
  gap?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8
  itemClassName?: string
  contentClassName?: string
}

function getGridColsFixed(n: Columns = 2) {
  const map: Record<Columns, string> = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
  }
  return map[n]
}

function getGapClass(gap?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8) {
  const map: Record<number, string> = {
    1: 'gap-1',
    2: 'gap-2',
    3: 'gap-3',
    4: 'gap-4',
    5: 'gap-5',
    6: 'gap-6',
    7: 'gap-7',
    8: 'gap-8',
  }
  return map[gap || 4] || 'gap-4'
}

function getPaddingBySize(size: Size = 'md') {
  // Сделаем sm заметно компактнее
  if (size === 'sm') return 'p-2'
  if (size === 'lg') return 'p-6'
  return 'p-4'
}

export default function QuickStats({
  items = ['totalPets', 'alivePets', 'deadPets', 'coins', 'status'],
  data,
  columns = 2,
  size = 'md',
  gap = 4,
  itemClassName,
  contentClassName,
}: QuickStatsProps) {
  const gridFixed = getGridColsFixed(columns)
  const gridGap = getGapClass(gap)
  const padding = getPaddingBySize(size)
  const isCompact = size === 'sm' || columns >= 4
  const iconSize = size === 'lg' ? 30 : size === 'sm' ? 20 : 26
  const valueClass = (size === 'lg' ? 'text-xl' : size === 'sm' ? 'text-base' : 'text-lg') + ' font-semibold leading-none'
  const labelClass = isCompact ? 'hidden' : 'text-sm text-slate-400'
  // Всегда центрируем иконку и значение по вертикали и горизонтали
  const rowClass = 'flex h-full flex-col items-center justify-center text-center space-y-1'

  const renderItem = (itemKey: QuickStatItem) => {
    const wrap = (uniqueKey: string, node: JSX.Element, to?: string) => (to ? (
      <Link key={uniqueKey} to={to} className="block">
        {node}
      </Link>
    ) : (
      <div key={uniqueKey}>{node}</div>
    ))

    switch (itemKey) {
      case 'totalPets':
        return wrap('totalPets', (
          <Card className={cn('cursor-pointer hover:border-primary-500 transition-colors', itemClassName)}>
            <CardContent className={cn(padding, contentClassName)}>
              <div className={rowClass}>
                <Users className="text-sky-400" size={iconSize} />
                <div className="space-y-0.5">
                  <p className={labelClass}>Всего</p>
                  <p className={cn(valueClass, 'text-sky-400')}>{data.totalPets}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ), '/history')
      case 'alivePets':
        return wrap('alivePets', (
          <Card className={cn('cursor-pointer hover:border-primary-500 transition-colors', itemClassName)}>
            <CardContent className={cn(padding, contentClassName)}>
              <div className={rowClass}>
                <Heart className="text-pink-400" size={iconSize} />
                <div className="space-y-0.5">
                  <p className={labelClass}>Живых</p>
                  <p className={cn(valueClass, 'text-pink-400')}>{data.alivePets ?? 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ), '/history')
      case 'deadPets':
        return wrap('deadPets', (
          <Card className={cn('cursor-pointer hover:border-primary-500 transition-colors', itemClassName)}>
            <CardContent className={cn(padding, contentClassName)}>
              <div className={rowClass}>
                <Skull className="text-white" size={iconSize} />
                <div className="space-y-0.5">
                  <p className={labelClass}>Мертвых</p>
                  <p className={cn(valueClass, 'text-white')}>{data.deadPets ?? 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ), '/history')
      case 'coins':
        return wrap('coins', (
          <Card className={cn('cursor-pointer hover:border-primary-500 transition-colors', itemClassName)}>
            <CardContent className={cn(padding, contentClassName)}>
              <div className={rowClass}>
                <Coins className="text-coin" size={iconSize} />
                <div className="space-y-0.5">
                  <p className={labelClass}>Монеты</p>
                  <p className={cn(valueClass, 'text-coin')}>{data.coins ?? 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ), '/economy')
      case 'status':
        return (
          <Card key="status" className={cn(itemClassName)}>
            <CardContent className={cn(padding, contentClassName)}>
              <div className={rowClass}>
                <div className="w-5 h-5 rounded-full bg-primary-600" />
                <div className="space-y-0.5">
                  <p className={labelClass}>Статус</p>
                  <p className={cn(valueClass, 'capitalize')}>{data.statusText ?? '—'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      default:
        return null
    }
  }

  return (
    <div className={cn('grid', gridFixed, gridGap)}>
      {items.map(renderItem)}
    </div>
  )
}

