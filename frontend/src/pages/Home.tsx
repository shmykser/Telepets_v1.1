import { useEffect, useState, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Plus, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
// import PetCard from '@/components/PetCard'
import PetCarousel from '@/components/PetCarousel'
import { usePet, useAllPets } from '@/hooks/usePet'
import { useWallet, useActionCosts } from '@/hooks/useEconomy'
import { getStoredUserId } from '@/utils'
import { notifyError } from '@/components/Notification'
import CreatePet from '@/components/CreatePet'
import QuickStats from '@/components/QuickStats'
import Welcome from '@/components/Welcome'
import AllDead from '@/components/AllDead'

export default function Home() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [petName, setPetName] = useState('')
  const [isCreatingPending, setIsCreatingPending] = useState(false)
  const [lastCreatedName, setLastCreatedName] = useState<string | null>(null)
  const prevPetsCountRef = useRef<number>(0)
  const [hadAliveAtCreate, setHadAliveAtCreate] = useState<boolean | null>(null)
  // ID пользователя используется в других местах приложения; на Главной не отображаем
  const [/* userId */, /* setUserId */] = useState(getStoredUserId())
  const location = useLocation()
  const navigate = useNavigate()
  
  const {
    pet,
    isLoading,
    error,
    createPet,
    healthUp,
    healthUpWithCost,
    resurrect,
    isCreating,
    isHealthUpLoading,
    isHealthUpWithCostLoading,
  } = usePet()

  // Открывать форму создания, если пришли со state.create=true из шапки
  useEffect(() => {
    const st: any = (location && (location as any).state) || {}
    if (st && st.create) {
      setShowCreateForm(true)
      // Сбросить state, чтобы при обновлении не открывалась снова
      navigate(location.pathname, { replace: true, state: {} })
    }
  }, [location, navigate])
  const { pets: allPets, isLoading: allLoading, wallet } = useAllPets()
  const { wallet: liveWallet } = useWallet()
  const { actionCosts } = useActionCosts()

  //

  // Снимаем индикатор, когда появился созданный питомец/увеличился список
  useEffect(() => {
    if (!isCreatingPending) return
    // Появился питомец с тем именем
    if (lastCreatedName && Array.isArray(allPets) && allPets.some((p: any) => p.name === lastCreatedName)) {
      setIsCreatingPending(false)
      setLastCreatedName(null)
      setHadAliveAtCreate(null)
      return
    }
    // Увеличилось число питомцев
    if (Array.isArray(allPets) && allPets.length > prevPetsCountRef.current) {
      setIsCreatingPending(false)
      setLastCreatedName(null)
      setHadAliveAtCreate(null)
      return
    }
    // Фолбэк по summary
    if (hadAliveAtCreate === false && pet && pet.status === 'success') {
      setIsCreatingPending(false)
      setLastCreatedName(null)
      setHadAliveAtCreate(null)
    }
  }, [isCreatingPending, pet, allPets, lastCreatedName, hadAliveAtCreate])

  useEffect(() => {
    if (Array.isArray(allPets)) {
      prevPetsCountRef.current = allPets.length
    }
  }, [allPets?.length])

  const handleCreatePet = (override = false) => {
    if (!petName.trim()) {
      notifyError('Введите имя питомца')
      return
    }
    // Показываем индикатор ожидания появления питомца в интерфейсе
    setIsCreatingPending(true)
    const name = petName.trim()
    setLastCreatedName(name)
    const hasAliveNow = Array.isArray(allPets) && allPets.some((p: any) => (p.status || p.life_status) !== 'dead')
    setHadAliveAtCreate(hasAliveNow)
    createPet({ name, override })
    setPetName('')
    setShowCreateForm(false)
  }

  // UserId управление перенесено в Настройки

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-slate-400">Загрузка питомца...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="text-red-400" />
              <span>Ошибка загрузки</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400 mb-4">
              Не удалось загрузить информацию о питомце. Возможно, у вас еще нет питомца.
            </p>
            <Button onClick={() => setShowCreateForm(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Создать питомца
            </Button>
          </CardContent>
        </Card>
        {showCreateForm && (
          <CreatePet
            petName={petName}
            setPetName={setPetName}
            onCreate={handleCreatePet}
            onCancel={() => setShowCreateForm(false)}
            isCreating={isCreating}
            canCreateFree={true}
            walletCoins={liveWallet?.coins ?? wallet?.coins}
            paidCost={(actionCosts?.action_costs as any)?.paid_pet ?? 500}
          />
        )}
      </div>
    )
  }

  // Обработка статусов от API
  if (!pet || pet.status === 'no_pets') {
    if (showCreateForm) {
      return (
        <div className="max-w-2xl mx-auto">
          <CreatePet
            petName={petName}
            setPetName={setPetName}
            onCreate={handleCreatePet}
            onCancel={() => setShowCreateForm(false)}
            isCreating={isCreating}
            canCreateFree={true}
            walletCoins={liveWallet?.coins ?? wallet?.coins}
            paidCost={(actionCosts?.action_costs as any)?.paid_pet ?? 500}
          />
        </div>
      )
    }
    return (
      <div className="max-w-2xl mx-auto">
        <Welcome onCreateClick={() => setShowCreateForm(true)} message={pet?.message} />
      </div>
    )
  }

  // Флаг: все питомцы мертвы — продолжаем показывать основной интерфейс, но добавим баннер
  const allDead = pet.status === 'all_dead'
  const hasAlive = Array.isArray(allPets) && allPets.some((p: any) => (p.status || p.life_status) !== 'dead')


  return (
    <div className="space-y-6">

      {/* Баннер о смерти всех питомцев (не скрывает основной интерфейс) */}
      {allDead && !showCreateForm && !isCreatingPending && !hasAlive && (
        <div className="max-w-2xl mx-auto">
          <AllDead
            totals={{ total_pets: pet.total_pets, dead_pets: pet.dead_pets || 0 }}
            message={pet.message}
            onCreateClick={() => setShowCreateForm(true)}
          />
        </div>
      )}

      {/* Индикатор создания нового питомца (оверлей поверх страницы) */}
      {isCreatingPending && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50">
          <div className="text-center bg-surface border border-border rounded-lg px-6 py-5 shadow-lg">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-3" />
            <p className="text-slate-200">Создаём питомца…</p>
          </div>
        </div>
      )}

      {/* Create Pet Form */}
      {showCreateForm && (
        <CreatePet
          petName={petName}
          setPetName={setPetName}
          onCreate={handleCreatePet}
          onCancel={() => setShowCreateForm(false)}
          isCreating={isCreating}
          canCreateFree={(() => {
            const alive = allPets.filter((p: any) => p.status !== 'dead')
            return alive.length === 0 || alive.every((p: any) => p.state === 'adult')
          })()}
          walletCoins={liveWallet?.coins ?? wallet?.coins}
          paidCost={(actionCosts?.action_costs as any)?.paid_pet ?? 500}
        />
      )}

      {/* Кнопка "Помощь питомцу" удалена — функционал в карточке */}

      
      {/* Quick Stats */}
      <QuickStats
        items={[ 'coins', 'alivePets', 'deadPets', 'totalPets']}
        //itemSpans={{ status: 2 }}
        data={{
          totalPets: pet.total_pets || 0,
          alivePets: pet.alive_pets,
          deadPets: pet.dead_pets,
          coins: pet.wallet?.coins,
          //statusText: pet.status === 'success' ? 'живой' : (pet.status ?? '—'),
        }}
        columns={4}
        size="sm"
      />

      {/* Карусель с карточками питомцев доступна всегда, если есть питомцы (даже если все мертвы) */}
      {!allLoading && allPets && allPets.length > 0 && (
        <PetCarousel
          pets={allPets}
          onSelect={() => {}}
          onHealthUp={(name) => healthUp(name)}
          onHealthUpWithCost={(name) => healthUpWithCost(name)}
          onResurrect={(name) => resurrect(name)}
          isHealthUpLoading={isHealthUpLoading}
          isHealthUpWithCostLoading={isHealthUpWithCostLoading}
          walletCoins={liveWallet?.coins ?? wallet?.coins}
          actionCosts={actionCosts?.action_costs as any}
        />
      )}

    </div>
  )
} 