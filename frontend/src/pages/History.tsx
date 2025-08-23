import { motion } from 'framer-motion'
import { History as HistoryIcon, Heart, Calendar, User } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useAllPets } from '@/hooks/usePet'
import { getStageInfo, formatDate } from '@/utils'
import HealthBar from '@/components/ui/HealthBar'

export default function History() {
  const { pets, wallet, totalPets, alivePets, deadPets, isLoading, error } = useAllPets()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-slate-400">Загрузка истории...</p>
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
              <HistoryIcon className="text-red-400" />
              <span>Ошибка загрузки</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400">
              Не удалось загрузить историю питомцев.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <User className="text-primary-400" size={20} />
              <div>
                <p className="text-sm text-slate-400">Всего питомцев</p>
                <p className="text-2xl font-bold">{totalPets}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Heart className="text-green-400" size={20} />
              <div>
                <p className="text-sm text-slate-400">Живых</p>
                <p className="text-2xl font-bold text-green-400">{alivePets}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Heart className="text-red-400" size={20} />
              <div>
                <p className="text-sm text-slate-400">Мертвых</p>
                <p className="text-2xl font-bold text-red-400">{deadPets}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {wallet && (
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 rounded-full bg-coin" />
                <div>
                  <p className="text-sm text-slate-400">Монеты</p>
                  <p className="text-2xl font-bold text-coin">{wallet.coins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Pets List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <HistoryIcon className="text-primary-400" />
            <span>История питомцев</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {pets.length > 0 ? (
            <div className="space-y-4">
              {pets.map((pet, index) => {
                const stageInfo = getStageInfo(pet.state || 'egg')
                const health = pet.health ?? 0
                
                return (
                  <motion.div
                    key={pet.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <div className="flex items-center justify-between p-4 rounded-lg border border-border hover:border-primary-500 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className="text-3xl">{stageInfo.emoji}</div>
                        <div>
                          <h3 className="font-semibold">{pet.name}</h3>
                          <div className="flex items-center space-x-2 text-sm text-slate-400">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${stageInfo.color}`}>
                              {stageInfo.name}
                            </span>
                            <span>•</span>
                            <span className="capitalize">{pet.status}</span>
                            <span>•</span>
                            <span>{pet.health ?? 0}/100</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        {/* Health bar */}
                        <div className="w-24">
                          <HealthBar value={health} />
                        </div>
                        
                        {/* Date */}
                        <div className="text-right">
                          <p className="text-sm font-medium">
                            {pet.created_at ? formatDate(pet.created_at) : ''}
                          </p>
                          {pet.updated_at && (
                            <p className="text-xs text-slate-400">
                              Обновлен: {pet.updated_at ? formatDate(pet.updated_at) : ''}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🥚</div>
              <p className="text-slate-400">У вас пока нет питомцев</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Timeline */}
      {pets.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="text-primary-400" />
              <span>Временная линия</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />
              
              <div className="space-y-6">
                {pets.map((pet, index) => {
                  const stageInfo = getStageInfo(pet.state || 'egg')
                  
                  return (
                    <motion.div
                      key={pet.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="relative flex items-start space-x-4"
                    >
                      {/* Timeline dot */}
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl ${
                        pet.status === 'dead' ? 'bg-red-600' : 'bg-primary-600'
                      }`}>
                        {stageInfo.emoji}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold">{pet.name}</h3>
                          <span className="text-sm text-slate-400">
                            {pet.created_at ? formatDate(pet.created_at) : ''}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400 mt-1">
                          {stageInfo.name} • {pet.health ?? 0}/100 здоровья
                        </p>
                        {pet.status === 'dead' && (
                          <p className="text-sm text-red-400 mt-1">
                            Питомец умер
                          </p>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 