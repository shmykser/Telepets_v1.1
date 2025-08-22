import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Info } from 'lucide-react'
import React from 'react'

export default function AboutGame() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Info className="text-primary-400" />
          <span>О игре</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="font-semibold mb-2">Telepets v1.1.0</h3>
          <p className="text-slate-400 mb-4">
            Современный тамагочи для Telegram Web App. Выращивайте виртуальных питомцев,
            выполняя условия для поддержания их здоровья на разных стадиях развития.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-semibold mb-2">Стадии развития</h4>
            <ul className="space-y-1 text-sm text-slate-400">
              <li>🥚 Яйцо (10 минут) — требует тепло</li>
              <li>👶 Детеныш (10 минут) — требует еду</li>
              <li>🧒 Подросток (10 минут) — требует отдых</li>
              <li>👨 Взрослый (финал) — требует внимание</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Система здоровья</h4>
            <ul className="space-y-1 text-sm text-slate-400">
              <li>Максимум: 100 единиц</li>
              <li>Критический уровень: 20 единиц</li>
              <li>Смерть: 0 единиц</li>
              <li>Автоматическое уменьшение: каждую минуту</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


