import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { notifySuccess, notifyError, notify } from '@/components/Notification'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import HealthBar from '@/components/ui/HealthBar'
import { Input } from '@/components/ui/Input'

import PetCard from '@/components/PetCard'
import UserId from '@/components/UserId'
import CreatePet from '@/components/CreatePet'
import QuickStats from '@/components/QuickStats'
import Welcome from '@/components/Welcome'
import AllDead from '@/components/AllDead'
import PetCarousel from '@/components/PetCarousel'

import ThemeSelector from '@/components/settings/ThemeSelector'
import AboutGame from '@/components/settings/AboutGame'
import ApiEndpointsList from '@/components/settings/ApiEndpointsList'
import DevInfo from '@/components/settings/DevInfo'

import type { Pet } from '@/types'

export default function ComponentsDemo() {
  const demoPet: Pet = {
    user_id: 'demo',
    name: 'bvc',
    state: 'adult',
    health: 84,
    status: 'success',
    total_pets: 1,
    wallet: { coins: 235, total_earned: 0, total_spent: 0 },
  }
  const demoPets: Pet[] = [
    { ...demoPet, id: 1, name: 'Alpha', state: 'egg', health: 62 },
    { ...demoPet, id: 2, name: 'Bravo', state: 'baby', health: 47 },
    { ...demoPet, id: 3, name: 'Charlie', state: 'adult', health: 91 },
  ]

  return (
    <div className="space-y-6">
      {/* UI primitives */}
      <Card>
        <CardHeader>
          <CardTitle>UI / Card.tsx</CardTitle>
        </CardHeader>
        <CardContent>Это пример карточки.</CardContent>
      </Card>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">UI / Button.tsx</div>
        <div className="flex gap-2 flex-wrap">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button loading>Loading</Button>
          <Button onClick={() => notifySuccess('Пример успешного уведомления')}>Показать успех</Button>
          <Button variant="secondary" onClick={() => notifyError('Пример ошибки')}>Показать ошибку</Button>
          <Button variant="ghost" onClick={() => notify('Пример уведомления')}>Показать уведомление</Button>
        </div>
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">UI / LoadingSpinner.tsx</div>
        <div className="flex items-center gap-6">
          <LoadingSpinner size="sm" />
          <LoadingSpinner size="md" />
          <LoadingSpinner size="lg" />
        </div>
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">UI / Input.tsx</div>
        <Input label="Поле ввода" placeholder="Введите текст" helperText="Подсказка" />
        <Input label="Поле с ошибкой" placeholder="Ошибка" error="Сообщение об ошибке" />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">UI / HealthBar.tsx</div>
        <div className="space-y-2">
          <HealthBar value={90} />
          <HealthBar value={55} />
          <HealthBar value={15} />
        </div>
      </div>

      {/* Domain components */}
      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / PetCard.tsx</div>
        <PetCard
          pet={demoPet}
          onHealthUp={() => {}}
          onHealthUpWithCost={() => {}}
          isHealthUpLoading={false}
          isHealthUpWithCostLoading={false}
          showCost={true}
        />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / UserId.tsx</div>
        <UserId userId={demoPet.user_id} onChange={() => {}} onSubmit={() => {}} />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / CreatePet.tsx</div>
        <CreatePet petName="" setPetName={() => {}} onCreate={() => {}} onCancel={() => {}} />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / QuickStats.tsx</div>
        <QuickStats data={{ totalPets: 3, alivePets: 2, deadPets: 1, coins: 235, statusText: 'живой' }} />
        <QuickStats items={["coins","status","totalPets"]} data={{ totalPets: 3, coins: 999, statusText: 'alive' }} />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / PetCarousel.tsx</div>
        <PetCarousel
          pets={demoPets}
          onSelect={() => {}}
          onHealthUp={() => {}}
          onHealthUpWithCost={() => {}}
          isHealthUpLoading={false}
          isHealthUpWithCostLoading={false}
        />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / Welcome.tsx</div>
        <Welcome onCreateClick={() => {}} />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components / AllDead.tsx</div>
        <AllDead totals={{ total_pets: 5, dead_pets: 5 }} onCreateClick={() => {}} />
      </div>

      {/* Settings blocks */}
      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components/settings / ThemeSelector.tsx</div>
        <ThemeSelector theme="dark" onChange={() => {}} />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components/settings / AboutGame.tsx</div>
        <AboutGame />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components/settings / ApiEndpointsList.tsx</div>
        <ApiEndpointsList />
      </div>

      <div className="space-y-2">
        <div className="text-slate-400 text-sm">components/settings / DevInfo.tsx</div>
        <DevInfo />
      </div>
    </div>
  )
}


