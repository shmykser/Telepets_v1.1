import { useRef, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/Dialog'
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
          className="fixed inset-0 z-50 bg-background"
          style={{ paddingTop: 'var(--tg-safe-top, 0px)', paddingBottom: 'var(--tg-safe-bottom, 0px)' }}
        >
          {/* Крестик выхода */}
          <button
            type="button"
            className="absolute top-3 right-3 p-2 rounded-md bg-surface/80 border border-border text-slate-200 hover:bg-surface"
            onClick={() => setConfirmExit(true)}
          >
            <X size={20} />
          </button>

          {/* Игровое поле (пока заглушка) */}
          <div className="absolute inset-0">
            {/* Яйцо снизу по центру */}
            <div className="absolute left-1/2 -translate-x-1/2" style={{ bottom: 'calc(16px + var(--tg-safe-bottom, 0px))' }}>
              <div className="text-6xl select-none">🥚</div>
            </div>
          </div>

          {/* Диалог подтверждения выхода */}
          <Dialog open={confirmExit} onOpenChange={setConfirmExit}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Выйти из игры?</DialogTitle>
                <DialogDescription>
                  Прогресс прототипа не сохраняется. Подтвердить выход?
                </DialogDescription>
              </DialogHeader>
              <div className="mt-4 flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setConfirmExit(false)}>Отмена</Button>
                <Button onClick={exitGame}>Выйти</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      )}
    </div>
  )
}


