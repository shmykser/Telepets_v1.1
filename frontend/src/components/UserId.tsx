import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import React from 'react'

interface UserIdProps {
  userId: string
  onChange: (newUserId: string) => void
  onSubmit: () => void
}

export default function UserId({ userId, onChange, onSubmit }: UserIdProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Настройки пользователя</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <Input
              label="ID пользователя"
              value={userId}
              onChange={(e) => onChange((e.target as HTMLInputElement).value)}
              placeholder="Введите ID пользователя"
            />
          </div>
          <Button onClick={onSubmit} disabled={!userId.trim()} className="mt-6">
            Обновить
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}


