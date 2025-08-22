import { useCallback, useEffect, useRef, useState } from 'react'

interface UseTimerOptions {
	/** Запускать таймер автоматически при монтировании и изменении initialSeconds */
	autoplay?: boolean
	/** Период тиков в миллисекундах */
	intervalMs?: number
	/** Вызывать колбэк по завершении (достижении нуля) */
	onComplete?: () => void
	/** Останавливать тики, когда вкладка не активна */
	pauseWhenHidden?: boolean
}

interface UseTimerApi {
	secondsLeft: number
	isRunning: boolean
	hasCompleted: boolean
	start: () => void
	pause: () => void
	reset: (nextSeconds?: number) => void
}

/**
 * Тикающий таймер обратного отсчёта в секундах.
 * Безопасно очищает интервал и поддерживает автозапуск/остановку и повторный запуск при смене входных данных.
 */
export function useTimer(initialSeconds?: number | null, options?: UseTimerOptions): UseTimerApi {
	const {
		autoplay = true,
		intervalMs = 1000,
		onComplete,
		pauseWhenHidden = true,
	} = options || {}

	const clampToNonNegative = (value: number) => (Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0)

	const [secondsLeft, setSecondsLeft] = useState<number>(clampToNonNegative(initialSeconds ?? 0))
	const [isRunning, setIsRunning] = useState<boolean>(Boolean(autoplay && (initialSeconds ?? 0) > 0))
	const [hasCompleted, setHasCompleted] = useState<boolean>(clampToNonNegative(initialSeconds ?? 0) === 0)

	const intervalRef = useRef<number | null>(null)
	const onCompleteRef = useRef<(() => void) | undefined>(onComplete)
	onCompleteRef.current = onComplete

	const clearTick = useCallback(() => {
		if (intervalRef.current !== null) {
			window.clearInterval(intervalRef.current)
			intervalRef.current = null
		}
	}, [])

	const tick = useCallback(() => {
		setSecondsLeft(prev => {
			if (prev <= 1) {
				// Дойдём до нуля и остановимся
				clearTick()
				setIsRunning(false)
				setHasCompleted(true)
				// Вызовём onComplete один раз
				if (onCompleteRef.current) {
					onCompleteRef.current()
				}
				return 0
			}
			return prev - 1
		})
	}, [clearTick])

	const start = useCallback(() => {
		if (isRunning || secondsLeft <= 0) return
		setIsRunning(true)
	}, [isRunning, secondsLeft])

	const pause = useCallback(() => {
		setIsRunning(false)
	}, [])

	const reset = useCallback((nextSeconds?: number) => {
		const next = clampToNonNegative(nextSeconds ?? initialSeconds ?? 0)
		setSecondsLeft(next)
		setHasCompleted(next === 0)
		setIsRunning(autoplay && next > 0)
	}, [autoplay, initialSeconds])

	// Управление интервалом
	useEffect(() => {
		clearTick()
		if (!isRunning) return
		// Не стартуем, если вкладка скрыта и включён pauseWhenHidden
		if (pauseWhenHidden && document.visibilityState === 'hidden') return
		intervalRef.current = window.setInterval(tick, intervalMs)
		return clearTick
	}, [isRunning, intervalMs, tick, clearTick, pauseWhenHidden])

	// Автостоп при скрытии вкладки
	useEffect(() => {
		if (!pauseWhenHidden) return
		const handleVisibility = () => {
			if (document.visibilityState === 'hidden') {
				clearTick()
			} else if (isRunning && intervalRef.current === null) {
				intervalRef.current = window.setInterval(tick, intervalMs)
			}
		}
		document.addEventListener('visibilitychange', handleVisibility)
		return () => document.removeEventListener('visibilitychange', handleVisibility)
	}, [intervalMs, isRunning, tick, clearTick, pauseWhenHidden])

	// Сброс при изменении initialSeconds
	useEffect(() => {
		setSecondsLeft(clampToNonNegative(initialSeconds ?? 0))
		setHasCompleted(clampToNonNegative(initialSeconds ?? 0) === 0)
		setIsRunning(autoplay && (initialSeconds ?? 0) > 0)
	}, [initialSeconds, autoplay])

	// Очистка при размонтировании
	useEffect(() => clearTick, [clearTick])

	return { secondsLeft, isRunning, hasCompleted, start, pause, reset }
}

export default useTimer


