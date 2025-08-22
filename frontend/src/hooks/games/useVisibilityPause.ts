import { useEffect } from 'react'

export function useVisibilityPause(onPause?: () => void, onResume?: () => void) {
  useEffect(() => {
    const handler = () => {
      if (document.hidden) onPause?.()
      else onResume?.()
    }
    document.addEventListener('visibilitychange', handler)
    return () => document.removeEventListener('visibilitychange', handler)
  }, [onPause, onResume])
}

export default useVisibilityPause


