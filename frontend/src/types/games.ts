export interface GameContext {
	userId: string
	petName?: string
	petStage?: string
	seed?: number
	difficulty?: 'easy' | 'normal' | 'hard'
	[key: string]: any
}

export interface GameInitOptions {
	container: HTMLElement
	width: number
	height: number
	context: GameContext
	onEvent?: (event: { type: string; payload?: any }) => void
}

export interface GameResult {
	score: number
	durationSec?: number
	meta?: Record<string, any>
}

export interface GameInstance {
	destroy: () => void
	resize?: (size: { width: number; height: number }) => void
	pause?: () => void
	resume?: () => void
	getResult?: () => GameResult | undefined
}

export type GameAdapter = (options: GameInitOptions) => Promise<GameInstance>


