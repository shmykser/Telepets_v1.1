import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Link } from 'react-router-dom'
import UserId from '@/components/UserId'
import { getStoredUserId, setStoredUserId } from '@/utils'
import ApiEndpointsList from '@/pages/Settings/ApiEndpointsList'
import DevInfo from '@/pages/Settings/DevInfo'

export default function Admin() {
  const [userId, setUserId] = useState(getStoredUserId())

  const handleUserIdChange = (newUserId: string) => {
    setUserId(newUserId)
    setStoredUserId(newUserId)
    window.location.reload()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Админка</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-slate-400 text-sm">Список полезных страниц:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <Link to="/components" className="text-primary-400 hover:underline">
                /components — демонстрация UI
              </Link>
            </li>
            <li>
              <Link to="/games/runner" className="text-primary-400 hover:underline">/games/runner</Link>
            </li>
            <li>
              <Link to="/games/puzzle" className="text-primary-400 hover:underline">/games/puzzle</Link>
            </li>
            <li>
              <Link to="/games/match3" className="text-primary-400 hover:underline">/games/match3</Link>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Настройки пользователя */}
      <UserId userId={userId} onChange={setUserId} onSubmit={() => handleUserIdChange(userId)} />

      {/* API Endpoints (актуальные) */}
      <ApiEndpointsList />

      {/* Информация для разработчиков (актуальная) */}
      <DevInfo />
    </div>
  )
}


