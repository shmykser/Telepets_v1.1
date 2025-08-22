import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import React from 'react'

export default function ApiEndpointsList() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>API Endpoints</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-green-400">POST /create</p>
            <p className="text-xs text-slate-400">Создание нового питомца</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-blue-400">POST /health_up</p>
            <p className="text-xs text-slate-400">Увеличение здоровья питомца</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-yellow-400">GET /summary</p>
            <p className="text-xs text-slate-400">Получение информации о питомце</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-yellow-400">GET /summary/all?user_id=</p>
            <p className="text-xs text-slate-400">Сводка всех питомцев пользователя</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-purple-400">GET /economy/wallet/{'{user_id}'}</p>
            <p className="text-xs text-slate-400">Получение информации о кошельке</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-purple-400">GET /economy/transactions/{'{user_id}'}?limit=</p>
            <p className="text-xs text-slate-400">История транзакций</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-purple-400">GET /economy/stats/{'{user_id}'}</p>
            <p className="text-xs text-slate-400">Статистика экономики пользователя</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-orange-400">POST /economy/purchase/{'{user_id}'}?package_id=</p>
            <p className="text-xs text-slate-400">Покупка монет (симуляция)</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-pink-400">GET /economy/actions/costs</p>
            <p className="text-xs text-slate-400">Стоимость действий и опции покупок</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-pink-400">POST /economy/actions/{'{user_id}'}/health_up?pet_name=</p>
            <p className="text-xs text-slate-400">Платное увеличение здоровья</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-red-400">POST /economy/actions/{'{user_id}'}/resurrect?pet_name=</p>
            <p className="text-xs text-slate-400">Воскрешение питомца</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-emerald-400">POST /economy/rewards/{'{user_id}'}/daily_login</p>
            <p className="text-xs text-slate-400">Ежедневная награда</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800">
            <p className="text-sm font-mono text-emerald-400">POST /economy/games/{'{user_id}'}/claim?game=&score=</p>
            <p className="text-xs text-slate-400">Награда за мини‑игры</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


