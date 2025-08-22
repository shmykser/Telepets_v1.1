import { useEffect } from 'react'

export function usePreventScroll() {
  useEffect(() => {
    const orig = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const prevent = (e: Event) => e.preventDefault()
    document.addEventListener('touchmove', prevent, { passive: false })
    return () => {
      document.body.style.overflow = orig
      document.removeEventListener('touchmove', prevent)
    }
  }, [])
}

export default usePreventScroll


