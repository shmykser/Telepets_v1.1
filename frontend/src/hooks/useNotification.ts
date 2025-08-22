import { notifySuccess, notifyError, notify as notifyInfo, notifyLoading, dismiss } from '@/components/Notification'

function extractErrorMessage(error: unknown, fallback?: string): string {
  const anyErr = error as any
  return (
    anyErr?.response?.data?.detail ||
    anyErr?.response?.data?.message ||
    anyErr?.message ||
    (typeof error === 'string' ? error : undefined) ||
    fallback ||
    'Произошла ошибка'
  )
}

export function useNotification() {
  return {
    success: (message: string) => notifySuccess(message),
    error: (errorOrMessage: unknown, fallback?: string) => notifyError(extractErrorMessage(errorOrMessage, fallback)),
    info: (message: string) => notifyInfo(message),
    loading: (message: string) => notifyLoading(message),
    dismiss,
    extractErrorMessage,
  }
}

export default useNotification


