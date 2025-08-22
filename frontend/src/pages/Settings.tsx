import ProfileSettings from '@/components/settings/ProfileSettings'
import ThemeSelector from '@/pages/Settings/ThemeSelector'
import AboutGame from '@/pages/Settings/AboutGame'
import { Settings as SettingsIcon } from 'lucide-react'
import React from 'react'

export default function Settings() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center space-x-3">
          <SettingsIcon size={32} />
          <span>Настройки</span>
        </h1>
        <p className="text-slate-600 mt-2">
          Управляйте настройками вашего профиля и аккаунта
        </p>
      </div>

      <div className="space-y-8">
        {/* Тема */}
        <ThemeSection />

        {/* Описание игры */}
        <AboutGame />

        {/* Профиль */}
        <ProfileSettings />
      </div>
    </div>
  )
} 

function ThemeSection() {
  const [theme, setTheme] = React.useState<'dark' | 'light' | 'system'>('system')

  React.useEffect(() => {
    const stored = localStorage.getItem('theme') as 'dark' | 'light' | 'system' | null
    if (stored) setTheme(stored)
  }, [])

  React.useEffect(() => {
    localStorage.setItem('theme', theme)
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else if (theme === 'light') {
      root.classList.remove('dark')
    } else {
      // system
      const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.toggle('dark', isDark)
    }
  }, [theme])

  return <ThemeSelector theme={theme} onChange={setTheme} />
}