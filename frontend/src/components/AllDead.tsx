import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { motion } from 'framer-motion'
//

interface AllDeadProps {
  totals: { total_pets: number; dead_pets: number }
  message?: string
  onCreateClick: () => void
}

export default function AllDead({ totals, message, onCreateClick }: AllDeadProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle className="text-center flex items-center justify-center space-x-2">
            <span>Все питомцы умерли</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <div className="text-6xl mb-4">💀</div>
          <p className="text-slate-400">{message || 'Все ваши питомцы умерли. Создайте нового!'}</p>
          <div className="text-sm text-slate-500">Всего питомцев: {totals.total_pets} | Мертвых: {totals.dead_pets}</div>
          <Button onClick={onCreateClick} size="lg">Создать нового питомца</Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}


