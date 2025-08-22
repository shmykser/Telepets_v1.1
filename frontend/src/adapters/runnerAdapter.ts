import type { GameAdapter, GameInitOptions, GameInstance } from '@/types/games'

export const runnerAdapter: GameAdapter = async ({ container, width, height, context }: GameInitOptions): Promise<GameInstance> => {
  const phaser = await import('phaser')
  const { AUTO, Scene, Game: PhaserGame } = phaser as any

  class SceneImpl extends (Scene as any) {
    score: number = 0
    player!: any
    cursors!: any
    constructor() { super('Runner') }
    preload() {
      this.load.image('bg', 'https://labs.phaser.io/assets/skies/space3.png')
      this.load.image('player', 'https://labs.phaser.io/assets/sprites/phaser-dude.png')
    }
    create() {
      const { width, height } = this.scale
      this.add.image(width/2, height/2, 'bg').setScrollFactor(0)
      this.player = this.add.sprite(width/2, height/2, 'player')
      this.physics.add.existing(this.player)
      this.cursors = this.input.keyboard.createCursorKeys()
    }
    update() {
      const body = this.player.body as any
      body.setVelocity(0)
      if (this.cursors.left.isDown) body.setVelocityX(-200)
      else if (this.cursors.right.isDown) body.setVelocityX(200)
      if (this.cursors.up.isDown) body.setVelocityY(-200)
      else if (this.cursors.down.isDown) body.setVelocityY(200)
    }
  }

  const game = new PhaserGame({
    type: AUTO,
    parent: container,
    width: Math.max(320, width),
    height: Math.max(480, height),
    backgroundColor: '#000',
    physics: { default: 'arcade', arcade: { gravity: { y: 0 }, debug: false } },
    scene: SceneImpl,
    scale: { mode: (phaser as any).Scale.RESIZE, autoCenter: (phaser as any).Scale.CENTER_BOTH },
  })

  return {
    destroy: () => { try { game.destroy(true) } catch {} },
    resize: ({ width, height }) => { try { game.scale.resize(width, height) } catch {} },
    pause: () => { try { (game.scene.keys as any).Runner?.scene?.pause() } catch {} },
    resume: () => { try { (game.scene.keys as any).Runner?.scene?.resume() } catch {} },
    getResult: () => ({ score: (game.scene.keys as any).Runner?.score ?? 0 }),
  }
}

export default runnerAdapter


