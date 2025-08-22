import { motion } from 'framer-motion'
import { Coins, TrendingUp, TrendingDown, Gift, DollarSign } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useWallet, useTransactions, useUserStats, useActionCosts, useDailyLogin, usePurchaseCoins } from '@/hooks/useEconomy'
import { formatDate } from '@/lib/utils'

export default function Economy() {
  const { wallet, isLoading: walletLoading } = useWallet()
  const { transactions, isLoading: transactionsLoading } = useTransactions(10)
  const { stats, isLoading: statsLoading } = useUserStats()
  const { actionCosts, isLoading: costsLoading } = useActionCosts()
  const { claimDailyLogin, isClaiming } = useDailyLogin()
  const { purchaseCoins, isPurchasing } = usePurchaseCoins()

  const purchaseOptions = [
    { id: 'coins_100', coins: 100, price: 0.99 },
    { id: 'coins_500', coins: 500, price: 3.99 },
    { id: 'coins_1000', coins: 1000, price: 6.99 },
    { id: 'coins_2500', coins: 2500, price: 14.99 },
    { id: 'coins_5000', coins: 5000, price: 24.99 },
  ]

  const handlePurchase = (packageId: string) => {
    purchaseCoins({ packageId })
  }

  if (walletLoading || statsLoading || costsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-slate-400">Загрузка экономики...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Wallet Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Coins className="text-coin" size={20} />
              <div>
                <p className="text-sm text-slate-400">Текущий баланс</p>
                <p className="text-2xl font-bold">{wallet?.coins || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="text-green-400" size={20} />
              <div>
                <p className="text-sm text-slate-400">Всего заработано</p>
                <p className="text-lg font-semibold">{wallet?.total_earned || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingDown className="text-red-400" size={20} />
              <div>
                <p className="text-sm text-slate-400">Всего потрачено</p>
                <p className="text-lg font-semibold">{wallet?.total_spent || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Daily Login Reward */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Gift className="text-yellow-400" />
            <span>Ежедневная награда</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 mb-4">
            Получайте 5 монет каждый день за вход в игру!
          </p>
          <Button
            onClick={() => claimDailyLogin()}
            loading={isClaiming}
            disabled={isClaiming}
          >
            Получить награду
          </Button>
        </CardContent>
      </Card>

      {/* Purchase Coins */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="text-green-400" />
            <span>Купить монеты</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {purchaseOptions.map((option) => (
              <motion.div
                key={option.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card className="cursor-pointer hover:border-primary-500 transition-colors">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl mb-2">🪙</div>
                    <h3 className="font-semibold mb-1">{option.coins} монет</h3>
                    <p className="text-sm text-slate-400 mb-3">${option.price}</p>
                    <Button
                      onClick={() => handlePurchase(option.id)}
                      loading={isPurchasing}
                      size="sm"
                      className="w-full"
                    >
                      Купить
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Action Costs */}
      {actionCosts && (
        <Card>
          <CardHeader>
            <CardTitle>Стоимость действий</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">Увеличение здоровья</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>🥚 Яйцо</span>
                    <span className="text-coin">{actionCosts.action_costs.health_up.egg} монет</span>
                  </div>
                  <div className="flex justify-between">
                    <span>👶 Детеныш</span>
                    <span className="text-coin">{actionCosts.action_costs.health_up.baby} монет</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🧒 Подросток</span>
                    <span className="text-coin">{actionCosts.action_costs.health_up.teen} монет</span>
                  </div>
                  <div className="flex justify-between">
                    <span>👨 Взрослый</span>
                    <span className="text-coin">{actionCosts.action_costs.health_up.adult} монет</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Дополнительные действия</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>🍎 Специальная еда</span>
                    <span className="text-coin">{actionCosts.action_costs.special_food} монет</span>
                  </div>
                  <div className="flex justify-between">
                    <span>💊 Лекарство</span>
                    <span className="text-coin">{actionCosts.action_costs.medicine} монет</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🧸 Игрушка</span>
                    <span className="text-coin">{actionCosts.action_costs.toy} монет</span>
                  </div>
                  <div className="flex justify-between">
                    <span>✂️ Уход</span>
                    <span className="text-coin">{actionCosts.action_costs.grooming} монет</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* User Stats */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Статистика</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold">{stats.total_pets}</p>
                <p className="text-sm text-slate-400">Всего питомцев</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-400">{stats.alive_pets}</p>
                <p className="text-sm text-slate-400">Живых</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-400">{stats.dead_pets}</p>
                <p className="text-sm text-slate-400">Мертвых</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{stats.total_transactions}</p>
                <p className="text-sm text-slate-400">Транзакций</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Последние транзакции</CardTitle>
        </CardHeader>
        <CardContent>
          {transactionsLoading ? (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
            </div>
          ) : transactions.length > 0 ? (
            <div className="space-y-3">
              {transactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      transaction.type === 'earning' || transaction.type === 'bonus'
                        ? 'bg-green-600'
                        : transaction.type === 'spending'
                        ? 'bg-red-600'
                        : 'bg-blue-600'
                    }`}>
                      {transaction.type === 'earning' || transaction.type === 'bonus' ? (
                        <TrendingUp size={16} className="text-white" />
                      ) : transaction.type === 'spending' ? (
                        <TrendingDown size={16} className="text-white" />
                      ) : (
                        <DollarSign size={16} className="text-white" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-slate-400">{formatDate(transaction.created_at)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${
                      transaction.type === 'earning' || transaction.type === 'bonus'
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      {transaction.type === 'earning' || transaction.type === 'bonus' ? '+' : '-'}
                      {transaction.amount} монет
                    </p>
                    <p className="text-xs text-slate-400">Баланс: {transaction.balance_after}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-slate-400 py-4">Нет транзакций</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 