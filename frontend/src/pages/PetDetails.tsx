import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Heart, Clock, Calendar } from 'lucide-react'
import { useState } from 'react'
import CreateAuctionModal from '@/components/market/CreateAuctionModal'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useAllPets } from '@/hooks/usePet'
import { getStageInfo, formatDate } from '@/utils'
import HealthBar from '@/components/ui/HealthBar'
import { Link } from 'react-router-dom'

export default function PetDetails() {
  const [showCreate, setShowCreate] = useState(false)
  const { petId } = useParams<{ petId: string }>()
  const { pets, isLoading, error } = useAllPets()
  
  const pet = pets.find(p => p.id && p.id.toString() === petId)

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

  if (error || !pet) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Heart className="text-red-400" />
              <span>Питомец не найден</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400 mb-4">
              Питомец с ID {petId} не найден.
            </p>
            <Link to="/">
              <Button>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Вернуться на главную
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const stageInfo = getStageInfo(pet.state || 'egg')
  const health = pet.health ?? 0

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div>
        <Link to="/">
          <Button variant="ghost" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад
          </Button>
        </Link>
      </div>

      {/* Pet Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-3">
                <span className="text-4xl">{stageInfo.emoji}</span>
                <div>
                  <h1 className="text-2xl font-bold">{pet.name}</h1>
                  <p className="text-slate-400">{stageInfo.name}</p>
                </div>
              </CardTitle>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${stageInfo.color}`}>
                {pet.status}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Health Section */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                <Heart className="text-red-400" />
                <span>Здоровье</span>
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Текущее здоровье</span>
                  <span className={"font-semibold"}>{pet.health}/100</span>
                </div>
                <HealthBar value={health} />
                <p className="text-sm text-slate-400">
                  {stageInfo.description}
                </p>
              </div>
            </div>

            {/* Stage Information */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                <Clock className="text-blue-400" />
                <span>Стадия развития</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Текущая стадия</p>
                  <p className="font-semibold">{stageInfo.name}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Описание</p>
                  <p className="font-semibold">{stageInfo.description}</p>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                <Calendar className="text-green-400" />
                <span>История</span>
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                      <span className="text-sm">🥚</span>
                    </div>
                    <div>
                      <p className="font-medium">Создан</p>
                          <p className="text-sm text-slate-400">{pet.created_at ? formatDate(pet.created_at) : ''}</p>
                    </div>
                  </div>
                </div>
                
                {pet.updated_at && (
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                        <span className="text-sm">📝</span>
                      </div>
                      <div>
                        <p className="font-medium">Последнее обновление</p>
                         <p className="text-sm text-slate-400">{pet.updated_at ? formatDate(pet.updated_at) : ''}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Status Alerts */}
            {pet.status === 'dead' && (
              <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/20">
                <p className="text-red-400 font-medium">Питомец умер</p>
                <p className="text-sm text-red-300 mt-1">
                  К сожалению, ваш питомец умер. Создайте нового питомца для продолжения игры.
                </p>
              </div>
            )}

            {pet.status === 'dying' && (
              <div className="p-4 rounded-lg bg-yellow-900/20 border border-yellow-500/20">
                <p className="text-yellow-400 font-medium">Критическое состояние</p>
                <p className="text-sm text-yellow-300 mt-1">
                  Ваш питомец в критическом состоянии! Срочно помогите ему!
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Related Pets */}
      {pets.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Другие питомцы</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {pets
                .filter(p => p.id !== pet.id)
                .slice(0, 3)
                .map((otherPet) => {
                  const otherStageInfo = getStageInfo(otherPet.state || 'egg')
                  return (
                    <Link
                      key={otherPet.id}
                      to={`/pet/${otherPet.id}`}
                      className="block p-4 rounded-lg border border-border hover:border-primary-500 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{otherStageInfo.emoji}</span>
                        <div>
                          <p className="font-medium">{otherPet.name}</p>
                          <p className="text-sm text-slate-400">
                            {otherStageInfo.name} • {otherPet.health}/100
                          </p>
                        </div>
                      </div>
                    </Link>
                  )
                })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Sell on Market */}
      {pet.status !== 'dead' && (
        <div>
          <Button onClick={() => setShowCreate(true)}>Продать на аукционе</Button>
        </div>
      )}
      {showCreate && (
        <CreateAuctionModal onClose={() => setShowCreate(false)} />
      )}
    </div>
  )
} 