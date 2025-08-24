import { useState } from 'react'
import { useAuctions } from '@/hooks/useEconomy'
import AuctionCard from '@/components/market/AuctionCard'
import CreateAuctionModal from '@/components/market/CreateAuctionModal'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import type { Auction } from '@/types'
import { Plus } from 'lucide-react'

export default function Market() {
  const [showCreate, setShowCreate] = useState(false)
  const { auctions, isLoading, error, refetch } = useAuctions('active', 1, 20)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Рынок питомцев</h1>
        <Button onClick={() => setShowCreate(true)}>Выставить питомца</Button>
      </div>

      {showCreate && (
        <CreateAuctionModal onClose={() => { setShowCreate(false); refetch() }} />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Активные аукционы</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-slate-400">Загрузка...</p>}
          {error && <p className="text-red-400">Ошибка загрузки</p>}
          {!isLoading && !error && auctions.length === 0 && (
            <p className="text-slate-400">Пока нет активных аукционов</p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {auctions
              .filter((a: Auction) => {
                // Скрываем лоты, у которых время истекло (0 секунд)
                const raw = (a.end_time as unknown as string) || ''
                const hasTz = /Z|[+-]\d{2}:?\d{2}$/.test(raw)
                const end = new Date(hasTz ? raw : `${raw}Z`).getTime()
                return end > Date.now()
              })
              .map((a: Auction) => (
              <AuctionCard key={a.id} auction={a} onAction={() => refetch()} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


