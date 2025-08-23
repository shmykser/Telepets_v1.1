import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useCreateAuction } from '@/hooks/useEconomy'
import { useAllPets } from '@/hooks/usePet'
import { getStoredUserId } from '@/utils'
import { X } from 'lucide-react'

export default function CreateAuctionModal({ onClose, initialPetId, onSubmitted }: { onClose: () => void; initialPetId?: number; onSubmitted?: () => void }) {
  const [petId, setPetId] = useState<number>(initialPetId || 0)
  const [startPrice, setStartPrice] = useState<number>(50)
  const [duration, setDuration] = useState<number>(3600)
  const [buyNowPrice, setBuyNowPrice] = useState<number>(0)
  const [showBuyNow, setShowBuyNow] = useState(false)

  const { createAuction, isCreating } = useCreateAuction()
  const { pets } = useAllPets()
  const availablePets = pets.filter((p: any) => {
    const status = (p.status || p.life_status || '').toString()
    return status === 'alive' || status === 'success'
  })

  useEffect(() => {
    if (initialPetId && pets.length > 0) {
      setPetId(initialPetId)
    }
  }, [initialPetId, pets.length])

  const handleSubmit = () => {
    if (petId === 0 || !startPrice) return
    createAuction({ 
      petId: Number(petId), 
      startPrice: Number(startPrice), 
      durationSeconds: Number(duration) || undefined, 
      buyNowPrice: buyNowPrice > 0 ? Number(buyNowPrice) : undefined 
    })
    onSubmitted?.()
    onClose()
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Выставить питомца на аукцион</DialogTitle>
          <DialogDescription>
            Заполните параметры лота и подтвердите размещение.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Питомец</label>
            <select 
              className="w-full rounded-md bg-surface border border-border px-3 py-2 text-sm"
              value={petId.toString()}
              onChange={(e) => setPetId(Number(e.target.value))}
            >
              <option value="0">Выберите питомца</option>
              {availablePets.map((pet: any) => (
                <option key={pet.id} value={pet.id.toString()}>
                  {pet.name} ({pet.state || pet.stage || 'unknown'})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Стартовая цена (монеты)</label>
            <Input 
              type="number" 
              value={startPrice.toString()} 
              onChange={(e) => setStartPrice(Number(e.target.value))}
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Длительность (секунды)</label>
            <Input 
              type="number" 
              value={duration.toString()} 
              onChange={(e) => setDuration(Number(e.target.value))}
              min="60"
              max="86400"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Купить сейчас (опционально)</label>
            <Input 
              type="number" 
              value={buyNowPrice.toString()} 
              onChange={(e) => setBuyNowPrice(Number(e.target.value))}
              min="0"
            />
          </div>

          <div className="flex space-x-3">
            <Button onClick={onClose} variant="outline" className="flex-1">
              Отмена
            </Button>
            <Button onClick={handleSubmit} disabled={isCreating || petId === 0 || pets.length === 0} className="flex-1">
              Выставить
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}


