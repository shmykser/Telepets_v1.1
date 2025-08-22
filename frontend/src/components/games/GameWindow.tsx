import { useEffect, useMemo, useRef, useState } from 'react'
import { useNotification } from '@/hooks/useNotification'
import { useFullscreen } from '@/hooks/games/useFullscreen'
import { usePreventScroll } from '@/hooks/games/usePreventScroll'
import { useVisibilityPause } from '@/hooks/games/useVisibilityPause'
import type { GameAdapter, GameContext, GameResult } from '@/types/games'
import { economyApi } from '@/lib/api'

interface GameWindowProps {
  title: string
  gameId: string
  adapter: GameAdapter
  context: GameContext
  autoFullscreen?: boolean
  claimOnEnd?: boolean
  showMenuButton?: boolean
}

export default function GameWindow({ title, gameId, adapter, context, autoFullscreen = true, claimOnEnd = true, showMenuButton = true }: GameWindowProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const wrapperRef = useRef<HTMLDivElement | null>(null)
  const instanceRef = useRef<{ destroy: () => void; resize?: (s: { width: number; height: number }) => void; pause?: () => void; resume?: () => void; getResult?: () => GameResult } | null>(null)
  const { success, error } = useNotification()
  const { isFullscreen, toggle } = useFullscreen(wrapperRef)
  usePreventScroll()

  const [size, setSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 })

  // Resize observer for wrapper
  useEffect(() => {
    const el = wrapperRef.current
    if (!el) return
    const obs = new ResizeObserver((entries) => {
      const r = entries[0].contentRect
      setSize({ width: Math.floor(r.width), height: Math.floor(r.height) })
      try { instanceRef.current?.resize?.({ width: Math.floor(r.width), height: Math.floor(r.height) }) } catch {}
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  useVisibilityPause(
    () => { try { instanceRef.current?.pause?.() } catch {} },
    () => { try { instanceRef.current?.resume?.() } catch {} },
  )

  // Boot game via adapter
  useEffect(() => {
    let disposed = false
    async function boot() {
      if (!containerRef.current) return
      try {
        const inst = await adapter({ container: containerRef.current, width: size.width, height: size.height, context, onEvent: undefined })
        if (disposed) { try { inst.destroy() } catch {}; return }
        instanceRef.current = inst
        if (autoFullscreen && !isFullscreen) {
          // fire and forget; user gesture might be required on iOS, so ignore errors
          toggle().catch(() => {})
        }
      } catch (e) {
        error(e, 'Ошибка запуска игры')
      }
    }
    boot()
    return () => {
      disposed = true
      try { instanceRef.current?.pause?.() } catch {}
      let result: GameResult | undefined
      try { result = instanceRef.current?.getResult?.() } catch {}
      try { instanceRef.current?.destroy() } catch {}
      instanceRef.current = null
      if (claimOnEnd && result && result.score > 0) {
        economyApi.claimGameReward(context.userId, gameId, result.score)
          .then((res) => success(`+${res.coins_added} монет`))
          .catch((e) => error(e, 'Не удалось начислить награду'))
      }
    }
  }, [adapter, autoFullscreen, claimOnEnd, context, error, gameId, isFullscreen, size.height, size.width, success, toggle])

  const header = useMemo(() => (
    <div className="absolute top-0 left-0 right-0 z-10 px-3 py-2 flex items-center justify-between bg-surface/60 backdrop-blur">
      <div className="text-sm text-slate-200 font-medium truncate">{title}</div>
      <div className="flex items-center gap-2">
        {showMenuButton && (
          <button className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-100" onClick={() => alert('Меню (демо)')}>Меню</button>
        )}
        <button className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-100" onClick={() => { try { instanceRef.current?.pause?.() } catch {}; history.back() }}>Выйти</button>
        <button className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-100" onClick={toggle}>{isFullscreen ? 'Окно' : 'Fullscreen'}</button>
      </div>
    </div>
  ), [isFullscreen, showMenuButton, title, toggle])

  return (
    <div className="fixed inset-0 z-50 bg-black">
      <div ref={wrapperRef} className="w-full h-[100dvh] max-h-[100dvh]">
        <div className="relative w-full h-full flex items-center justify-center">
          {header}
          <div
            ref={containerRef}
            className="relative w-full h-full"
            style={{ paddingTop: 'env(safe-area-inset-top)', paddingBottom: 'env(safe-area-inset-bottom)' }}
          />
        </div>
      </div>
    </div>
  )
}


