import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import React from 'react'

export default function DevInfo() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Информация для разработчиков</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          <p><strong>Backend:</strong> FastAPI + SQLAlchemy + SQLite</p>
          <p><strong>Frontend:</strong> React + TypeScript + Tailwind CSS</p>
          <p><strong>Анимации:</strong> Framer Motion</p>
          <p><strong>Состояние:</strong> React Query</p>
          <p><strong>Сборка:</strong> Vite</p>
          <p><strong>Игры:</strong> Phaser 3 (Canvas/WebGL), адаптеры под <code>GameWindow</code></p>
          <p><strong>Интеграция Telegram:</strong> WebApp (портрет, touch), haptics/MainButton — планируется</p>
          <p><strong>Экономика:</strong> эндпоинт наград за игры <code>POST /economy/games/{'{user_id}'}/claim</code></p>
        </div>
      </CardContent>
    </Card>
  )
}


