import type { GameAdapter, GameInitOptions, GameInstance } from '@/types/games'

type Cell = { x: number; y: number; color: number; sprite?: any }

export const match3Adapter: GameAdapter = async ({ container, width, height, context }: GameInitOptions): Promise<GameInstance> => {
  const phaser = await import('phaser')
  const { AUTO, Scene, Game: PhaserGame } = phaser as any

  class Match3Scene extends (Scene as any) {
    cols = 6
    rows = 8
    cellSize = 56
    board: Cell[][] = []
    colors = [0xEF4444, 0xF59E0B, 0x10B981, 0x3B82F6, 0x8B5CF6]
    score: number = 0
    scoreText!: any
    selected: Cell | null = null
    gridOrigin = { x: 0, y: 0 }

    constructor() { super('Match3') }

    create() {
      // Adjust grid by difficulty
      const diff: string | undefined = (context as any)?.difficulty
      if (diff === 'easy') { this.cols = 6; this.rows = 8 }
      else if (diff === 'hard') { this.cols = 7; this.rows = 10 }
      else { this.cols = 6; this.rows = 9 }

      this.computeLayout()
      this.scoreText = this.add.text(12, 12, 'Score: 0', { color: '#fff' }).setDepth(10)
      this.initBoard()
      this.input.on('pointerdown', (p: any) => this.onPointer(p))
      this.input.on('pointerup', (p: any) => this.onPointerUp(p))
      this.input.on('pointermove', (p: any) => this.onDrag(p))
    }

    resizeTo(width: number, height: number) {
      this.scale.resize(width, height)
      this.computeLayout()
      this.redrawBoard()
      this.scoreText?.setPosition(12, 12)
    }

    computeLayout() {
      const safeTop = 0
      const top = safeTop + 48
      const usableW = this.scale.width
      const usableH = this.scale.height - top - 24
      const cell = Math.min(Math.floor(usableW / this.cols), Math.floor(usableH / this.rows))
      this.cellSize = Math.max(36, Math.min(72, cell))
      const gridW = this.cols * this.cellSize
      const gridH = this.rows * this.cellSize
      this.gridOrigin.x = Math.floor((this.scale.width - gridW) / 2)
      this.gridOrigin.y = Math.floor(top + (usableH - gridH) / 2)
    }

    initBoard() {
      // Create board without initial matches
      this.board = []
      for (let y = 0; y < this.rows; y++) {
        const row: Cell[] = []
        for (let x = 0; x < this.cols; x++) {
          let colorIndex: number
          do {
            colorIndex = Math.floor(Math.random() * this.colors.length)
          } while (
            (x >= 2 && row[x-1]?.color === this.colors[colorIndex] && row[x-2]?.color === this.colors[colorIndex]) ||
            (y >= 2 && this.board[y-1]?.[x]?.color === this.colors[colorIndex] && this.board[y-2]?.[x]?.color === this.colors[colorIndex])
          )
          row.push({ x, y, color: this.colors[colorIndex] })
        }
        this.board.push(row)
      }
      this.drawBoard()
    }

    drawBoard() {
      for (let y = 0; y < this.rows; y++) {
        for (let x = 0; x < this.cols; x++) {
          const cell = this.board[y][x]
          if (!cell.sprite) {
            const spr = this.add.rectangle(0, 0, this.cellSize - 6, this.cellSize - 6, cell.color).setOrigin(0)
            spr.setX(this.gridOrigin.x + x * this.cellSize + 3)
            spr.setY(this.gridOrigin.y + y * this.cellSize + 3)
            spr.setInteractive({ useHandCursor: true })
            cell.sprite = spr
          } else {
            this.tweens.add({ targets: cell.sprite, x: this.gridOrigin.x + x * this.cellSize + 3, y: this.gridOrigin.y + y * this.cellSize + 3, duration: 120 })
          }
        }
      }
    }

    redrawBoard() {
      for (let y = 0; y < this.rows; y++) {
        for (let x = 0; x < this.cols; x++) {
          const cell = this.board[y][x]
          if (cell.sprite) {
            cell.sprite.setSize(this.cellSize - 6, this.cellSize - 6)
            cell.sprite.setX(this.gridOrigin.x + x * this.cellSize + 3)
            cell.sprite.setY(this.gridOrigin.y + y * this.cellSize + 3)
          }
        }
      }
    }

    screenToCell(px: number, py: number): Cell | null {
      const x = Math.floor((px - this.gridOrigin.x) / this.cellSize)
      const y = Math.floor((py - this.gridOrigin.y) / this.cellSize)
      if (x < 0 || x >= this.cols || y < 0 || y >= this.rows) return null
      return this.board[y][x]
    }

    onPointer(p: any) {
      const cell = this.screenToCell(p.x, p.y)
      if (!cell) return
      this.selected = cell
      cell.sprite?.setStrokeStyle(3, 0xffffff)
    }

    onDrag(p: any) {
      if (!this.selected) return
      const dx = p.x - (this.gridOrigin.x + this.selected.x * this.cellSize + this.cellSize/2)
      const dy = p.y - (this.gridOrigin.y + this.selected.y * this.cellSize + this.cellSize/2)
      if (Math.abs(dx) > this.cellSize * 0.4 || Math.abs(dy) > this.cellSize * 0.4) {
        const dirX = Math.abs(dx) > Math.abs(dy) ? Math.sign(dx) : 0
        const dirY = Math.abs(dy) >= Math.abs(dx) ? Math.sign(dy) : 0
        const tx = this.selected.x + dirX
        const ty = this.selected.y + dirY
        if (tx >= 0 && tx < this.cols && ty >= 0 && ty < this.rows) {
          this.trySwap(this.selected, this.board[ty][tx])
        }
        this.clearSelection()
      }
    }

    onPointerUp(_p: any) { this.clearSelection() }

    clearSelection() { if (this.selected) { this.selected.sprite?.setStrokeStyle(); this.selected = null } }

    trySwap(a: Cell, b: Cell) {
      // swap in board
      const tmp = a.color; a.color = b.color; b.color = tmp
      this.refreshSprites([a, b])
      const matches = this.findMatches()
      if (matches.length === 0) {
        // swap back
        const t2 = a.color; a.color = b.color; b.color = t2
        this.refreshSprites([a, b])
        return
      }
      this.resolveMatches(matches)
    }

    refreshSprites(cells: Cell[]) {
      for (const c of cells) { c.sprite?.setFillStyle(c.color) }
    }

    findMatches(): Cell[][] {
      const groups: Cell[][] = []
      // Horizontal
      for (let y = 0; y < this.rows; y++) {
        let run: Cell[] = [this.board[y][0]]
        for (let x = 1; x < this.cols; x++) {
          const prev = this.board[y][x-1]
          const curr = this.board[y][x]
          if (curr.color === prev.color) {
            run.push(curr)
          } else {
            if (run.length >= 3) groups.push(run)
            run = [curr]
          }
        }
        if (run.length >= 3) groups.push(run)
      }
      // Vertical
      for (let x = 0; x < this.cols; x++) {
        let run: Cell[] = [this.board[0][x]]
        for (let y = 1; y < this.rows; y++) {
          const prev = this.board[y-1][x]
          const curr = this.board[y][x]
          if (curr.color === prev.color) {
            run.push(curr)
          } else {
            if (run.length >= 3) groups.push(run)
            run = [curr]
          }
        }
        if (run.length >= 3) groups.push(run)
      }
      // Deduplicate cells: merge overlapping groups
      const uniqueGroups: Cell[][] = []
      const marked = new Set<string>()
      for (const g of groups) {
        const filtered = g.filter(c => {
          const k = `${c.x},${c.y}`
          if (marked.has(k)) return false
          marked.add(k); return true
        })
        if (filtered.length >= 3) uniqueGroups.push(filtered)
      }
      return uniqueGroups
    }

    async resolveMatches(groups: Cell[][]) {
      let removed = 0
      for (const g of groups) {
        removed += g.length
        for (const c of g) {
          // mark as empty using color -1
          c.color = -1 as any
          this.tweens.add({ targets: c.sprite, scale: 0.1, alpha: 0.2, duration: 120, onComplete: () => c.sprite?.destroy() })
          c.sprite = undefined
        }
      }
      this.score += removed * 10
      this.scoreText.setText(`Score: ${this.score}`)

      // drop down
      for (let x = 0; x < this.cols; x++) {
        let writeY = this.rows - 1
        for (let y = this.rows - 1; y >= 0; y--) {
          if (this.board[y][x].color !== -1) {
            if (writeY !== y) {
              const target = this.board[writeY][x]
              target.color = this.board[y][x].color
              target.sprite = this.board[y][x].sprite
              if (target.sprite) { target.sprite.setScale(1).setAlpha(1) }
              this.board[y][x].sprite = undefined
              this.board[y][x].color = -1 as any
            }
            writeY--
          }
        }
        // fill new
        for (let y = writeY; y >= 0; y--) {
          const color = this.colors[Math.floor(Math.random() * this.colors.length)]
          this.board[y][x].color = color
        }
      }
      this.drawBoard()

      // chain reactions
      const next = this.findMatches()
      if (next.length > 0) {
        await this.time.delayedCall(140, () => this.resolveMatches(next))
      }
    }
  }

  const game = new PhaserGame({
    type: AUTO,
    parent: container,
    width: Math.max(320, width),
    height: Math.max(480, height),
    backgroundColor: '#0b1220',
    scene: Match3Scene,
    scale: { mode: (phaser as any).Scale.RESIZE, autoCenter: (phaser as any).Scale.CENTER_BOTH },
  })

  return {
    destroy: () => { try { game.destroy(true) } catch {} },
    resize: ({ width, height }) => { try { game.scale.resize(width, height); (game.scene.keys as any).Match3?.resizeTo?.(width, height) } catch {} },
    pause: () => { try { (game.scene.keys as any).Match3?.scene?.pause() } catch {} },
    resume: () => { try { (game.scene.keys as any).Match3?.scene?.resume() } catch {} },
    getResult: () => ({ score: (game.scene.keys as any).Match3?.score ?? 0 }),
  }
}

export default match3Adapter


