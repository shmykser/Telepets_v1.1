import { useRef, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { X } from 'lucide-react'

export default function GamesEgg() {
  const [started, setStarted] = useState(false)
  const [confirmExit, setConfirmExit] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)

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
          style={{ paddingTop: 'var(--tg-safe-top, 0px)', paddingBottom: 'var(--tg-safe-bottom, 0px)' }}
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

          {/* Игровое поле (пока заглушка) */}
          <div className="absolute inset-0 z-[900] pointer-events-none">
            {/* Яйцо снизу по центру */}
            <div className="absolute left-1/2 -translate-x-1/2" style={{ bottom: 'calc(16px + var(--tg-safe-bottom, 0px))' }}>
              <div className="text-6xl select-none">🥚</div>
            </div>
          </div>

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


