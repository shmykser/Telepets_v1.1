// Простые функции для уведомлений
export const notifySuccess = (message: string) => {
  // В будущем можно заменить на toast библиотеку
  console.log('✅', message)
  alert(`✅ ${message}`)
}

export const notifyError = (message: string) => {
  // В будущем можно заменить на toast библиотеку
  console.error('❌', message)
  alert(`❌ ${message}`)
}

export const notifyInfo = (message: string) => {
  // В будущем можно заменить на toast библиотеку
  console.info('ℹ️', message)
  alert(`ℹ️ ${message}`)
}
