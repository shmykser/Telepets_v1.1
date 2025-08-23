import { getStoredUserId } from '@/utils'
import GameWindow from '@/components/games/GameWindow'
import { runnerAdapter } from '@/adapters/runnerAdapter'

export default function GamesRunner() {
  const userId = getStoredUserId()
  return (
    <GameWindow
      title="Runner"
      gameId="runner"
      adapter={runnerAdapter}
      context={{ userId, difficulty: 'normal' }}
      autoFullscreen
      claimOnEnd
      showMenuButton
    />
  )
}


