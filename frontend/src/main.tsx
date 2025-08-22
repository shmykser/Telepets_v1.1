import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider, setLogger } from 'react-query'
import Notification from '@/components/Notification'
import App from './App.tsx'
import './index.css'
import { initializeFonts } from '@/lib/fonts'

// Инициализируем шрифты для предотвращения зависания
initializeFonts();

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Подавляем ожидаемые 400 (недостаточно монет) из платного действия, чтобы не засорять консоль
setLogger({
  log: console.log,
  warn: console.warn,
  error: (error) => {
    const err: any = error as any
    const status = err?.response?.status
    const detail: string | undefined = err?.response?.data?.detail
    if (status === 400 && typeof detail === 'string' && detail.includes('Недостаточно монет')) {
      return
    }
    console.error(error)
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Notification />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
) 