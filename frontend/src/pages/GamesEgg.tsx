import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { X } from 'lucide-react'
import Phaser from 'phaser'
import Hammer from 'hammerjs'

export default function GamesEgg() {
  const [started, setStarted] = useState(false)
  const [confirmExit, setConfirmExit] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const phaserRef = useRef<Phaser.Game | null>(null)

  const handleStart = async () => {
    setStarted(true)
    try {
      const el = containerRef.current
      if (el && el.requestFullscreen) {
        await el.requestFullscreen().catch(() => {})
      }
      // На всякий случай блокируем прокрутку фона
      document.body.style.overflow = 'hidden'
    } catch {}
  }

  const exitGame = async () => {
    setConfirmExit(false)
    setStarted(false)
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen().catch(() => {})
      }
    } catch {}
    document.body.style.overflow = ''
  }

  useEffect(() => {
    if (!started || phaserRef.current) return
    const parent = containerRef.current
    if (!parent) return

    class EggScene extends Phaser.Scene {
      trees: Phaser.GameObjects.Text[] = []
      egg!: Phaser.GameObjects.Text
      constructor() { super('EggScene') }
      create() {
        const w = this.scale.width
        const h = this.scale.height
        this.add.rectangle(w/2, h/2, w, h, 0x0b1220)
        this.egg = this.add.text(w/2, h - 60, '🥚', { fontSize: '64px' }).setOrigin(0.5)
      }
      addTree(x: number, y: number) {
        const t = this.add.text(x, y, '🌳', { fontSize: '80px' }).setOrigin(0.5)
        this.trees.push(t)
      }
    }

    const game = new Phaser.Game({
      type: Phaser.AUTO,
      parent,
      width: parent.clientWidth,
      height: parent.clientHeight,
      backgroundColor: '#0b1220',
      scene: [EggScene],
    })
    phaserRef.current = game

    const hammer = new Hammer.Manager(parent)
    const press = new Hammer.Press({ time: 1000 })
    hammer.add(press)
    hammer.on('press', (ev: any) => {
      const rect = parent.getBoundingClientRect()
      let x = ev.center.x - rect.left
      let y = ev.center.y - rect.top
      // безопасная рабочая зона, чтобы верх/низ не обрезались
      const margin = 40
      x = Math.max(margin, Math.min(parent.clientWidth - margin, x))
      y = Math.max(margin, Math.min(parent.clientHeight - margin, y))
      const scene: any = game.scene.getScene('EggScene')
      if (scene?.addTree) scene.addTree(x, y)
    })

    const onResize = () => {
      game.scale.resize(parent.clientWidth, parent.clientHeight)
    }
    window.addEventListener('resize', onResize)

    return () => {
      window.removeEventListener('resize', onResize)
      hammer.destroy()
      try { game.destroy(true) } catch {}
      phaserRef.current = null
    }
  }, [started])

  return (
    <div className="p-4">
      {!started && (
        <div className="flex items-center justify-center">
          <Button size="lg" onClick={handleStart}>Старт</Button>
        </div>
      )}

      {started && (
        <div
          ref={containerRef}
          className="fixed inset-0 z-[900] bg-background"
        >
          {/* Крестик выхода */}
          <button
            type="button"
            className="absolute top-3 right-3 z-[950] p-2 rounded-md bg-surface/80 border border-border text-slate-200 hover:bg-surface pointer-events-auto"
            onClick={() => setConfirmExit(true)}
            onTouchStart={() => setConfirmExit(true)}
          >
            <X size={20} />
          </button>

          {/* Phaser инициализируется поверх этого контейнера */}

          {/* Кастомный модальный диалог поверх всего */}
          {confirmExit && (
            <div className="fixed inset-0 z-[2000] flex items-center justify-center">
              <div className="absolute inset-0 bg-black/60" onClick={() => setConfirmExit(false)} />
              <div className="relative z-[2001] w-[92%] max-w-sm rounded-lg border border-border bg-background p-5 shadow-xl">
                <div className="text-lg font-semibold">Выйти из игры?</div>
                <p className="mt-1 text-sm text-slate-400">Прогресс прототипа не сохраняется. Подтвердить выход?</p>
                <div className="mt-4 flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setConfirmExit(false)}>Отмена</Button>
                  <Button onClick={exitGame}>Выйти</Button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


