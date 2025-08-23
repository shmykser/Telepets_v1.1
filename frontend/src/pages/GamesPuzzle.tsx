import { getStoredUserId } from '@/utils'
import GameWindow from '@/components/games/GameWindow'
import { puzzleAdapter } from '@/adapters/puzzleAdapter'

export default function GamesPuzzle() {
  const userId = getStoredUserId()
  return (
    <GameWindow
      title="Puzzle"
      gameId="puzzle"
      adapter={puzzleAdapter}
      context={{ userId, difficulty: 'easy' }}
      autoFullscreen
      claimOnEnd
      showMenuButton
    />
  )
}


