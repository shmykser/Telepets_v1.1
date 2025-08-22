import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { motion } from 'framer-motion'
//

interface CreatePetProps {
  petName: string
  setPetName: (name: string) => void
  onCreate: (override?: boolean) => void
  onCancel: () => void
  isCreating?: boolean
  // новые пропсы для логики стоимости
  canCreateFree?: boolean // все живые adult или все мертвы
  walletCoins?: number // баланс игрока
  paidCost?: number // стоимость платного создания из настроек (для отображения)
}

export default function CreatePet({ petName, setPetName, onCreate, onCancel, isCreating, canCreateFree = false, walletCoins, paidCost = 0 }: CreatePetProps) {
  const hasName = Boolean(petName.trim())
  const requiredCost = canCreateFree ? 0 : (paidCost || 0)
  // Если стоимость > 0 и баланс неизвестен — считаем, что монет недостаточно (кнопка неактивна)
  const canAfford = requiredCost === 0 ? true : (typeof walletCoins === 'number' ? walletCoins >= requiredCost : false)
  const showFree = hasName && requiredCost === 0
  const showPaid = hasName && requiredCost > 0 && canAfford
  const disabled = !(hasName && canAfford)

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
      <Card>
        <CardHeader>
          <CardTitle>Создать нового питомца</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            value={petName}
            onChange={(e) => setPetName((e.target as HTMLInputElement).value)}
            placeholder="Введите имя питомца"
            onKeyPress={(e) => e.key === 'Enter' && onCreate()}
          />
          <div className="flex space-x-2 items-center">
            <Button
              onClick={() => onCreate(false)}
              loading={isCreating}
              disabled={disabled}
              className="flex-1 flex-col py-3"
            >
              <span className="text-base font-semibold">Создать</span>
              <span className="text-xs text-slate-300">
                {showFree && 'Бесплатно'}
                {showPaid && `${requiredCost} монет`}
                {hasName && requiredCost > 0 && !canAfford && `${requiredCost} монет`}
              </span>
            </Button>
            <Button onClick={onCancel} variant="secondary" className="flex-1">
              Отмена
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}


