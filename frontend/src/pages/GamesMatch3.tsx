import { getStoredUserId } from '@/utils'
import GameWindow from '@/components/games/GameWindow'
import { match3Adapter } from '@/adapters/match3Adapter'

export default function GamesMatch3() {
  const userId = getStoredUserId()
  return (
    <GameWindow
      title="Match-3"
      gameId="match3"
      adapter={match3Adapter}
      context={{ userId, difficulty: 'normal' }}
      autoFullscreen
      claimOnEnd
      showMenuButton
    />
  )
}


