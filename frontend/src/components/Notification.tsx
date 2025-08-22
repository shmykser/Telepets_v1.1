import { Toaster, toast } from 'react-hot-toast'

// Единая точка для уведомлений в приложении
// Используйте экспортируемые функции ниже для показа уведомлений из любого места

// Централизованный контроль количества одновременно видимых уведомлений
const MAX_TOASTS = 3
const activeToastIds: string[] = []

function registerToast(id: string) {
  activeToastIds.push(id)
  if (activeToastIds.length > MAX_TOASTS) {
    const oldestId = activeToastIds.shift()
    if (oldestId) {
      toast.dismiss(oldestId)
    }
  }
  return id
}

export function notifySuccess(message: string) {
  const id = toast.success(message)
  return registerToast(id)
}

export function notifyError(message: string) {
  const id = toast.error(message)
  return registerToast(id)
}

export function notify(message: string) {
  const id = toast(message)
  return registerToast(id)
}

export function notifyLoading(message: string) {
  const id = toast.loading(message)
  return registerToast(id)
}

export function dismiss(id?: string) {
  if (!id) {
    // Сбрасываем все
    activeToastIds.splice(0, activeToastIds.length)
  } else {
    const idx = activeToastIds.indexOf(id)
    if (idx >= 0) activeToastIds.splice(idx, 1)
  }
  toast.dismiss(id)
}

// Компонент-тостер. Разместите его один раз (например, в Layout или App)
export default function Notification() {
  return (
    <Toaster
      position="top-center"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1e293b',
          color: '#f8fafc',
          border: '1px solid #334155',
        },
      }}
    />
  )
}


