import type { GameAdapter, GameInitOptions, GameInstance } from '@/types/games'

export const puzzleAdapter: GameAdapter = async ({ container, width, height, context }: GameInitOptions): Promise<GameInstance> => {
  const phaser = await import('phaser')
  const { AUTO, Scene, Game: PhaserGame } = phaser as any

  class SceneImpl extends (Scene as any) {
    score: number = 0
    tiles!: any[]
    constructor() { super('Puzzle') }
    preload() { this.load.image('tile', 'https://labs.phaser.io/assets/sprites/block.png') }
    create() {
      const cols = 3, rows = 5
      const size = Math.min(this.scale.width, this.scale.height) / Math.max(cols, rows) - 4
      this.tiles = []
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const tile = this.add.sprite(40 + x*(size+4), 80 + y*(size+4), 'tile').setDisplaySize(size, size).setInteractive({ useHandCursor: true })
          tile.on('pointerdown', () => { this.score += 1; this.tweens.add({ targets: tile, angle: tile.angle + 90, duration: 120 }) })
          this.tiles.push(tile)
        }
      }
    }
  }

  const game = new PhaserGame({
    type: AUTO,
    parent: container,
    width: Math.max(320, width),
    height: Math.max(480, height),
    backgroundColor: '#111827',
    scene: SceneImpl,
    scale: { mode: (phaser as any).Scale.RESIZE, autoCenter: (phaser as any).Scale.CENTER_BOTH },
  })

  return {
    destroy: () => { try { game.destroy(true) } catch {} },
    resize: ({ width, height }) => { try { game.scale.resize(width, height) } catch {} },
    pause: () => { try { (game.scene.keys as any).Puzzle?.scene?.pause() } catch {} },
    resume: () => { try { (game.scene.keys as any).Puzzle?.scene?.resume() } catch {} },
    getResult: () => ({ score: (game.scene.keys as any).Puzzle?.score ?? 0 }),
  }
}

export default puzzleAdapter


