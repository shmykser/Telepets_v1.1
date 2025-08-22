import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Moon, Sun, Monitor } from 'lucide-react'
import React from 'react'

interface ThemeSelectorProps {
  theme: 'dark' | 'light' | 'system'
  onChange: (t: 'dark' | 'light' | 'system') => void
}

export default function ThemeSelector({ theme, onChange }: ThemeSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Monitor className="text-primary-400" />
          <span>Внешний вид</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button onClick={() => onChange('light')} className={`p-4 rounded-lg border-2 transition-colors ${theme === 'light' ? 'border-primary-500 bg-primary-500/10' : 'border-border hover:border-primary-500'}`}>
            <div className="flex items-center space-x-2 mb-2">
              <Sun size={20} />
              <span className="font-medium">Светлая</span>
            </div>
            <p className="text-sm text-slate-400">Классическая светлая тема</p>
          </button>

          <button onClick={() => onChange('dark')} className={`p-4 rounded-lg border-2 transition-colors ${theme === 'dark' ? 'border-primary-500 bg-primary-500/10' : 'border-border hover:border-primary-500'}`}>
            <div className="flex items-center space-x-2 mb-2">
              <Moon size={20} />
              <span className="font-medium">Темная</span>
            </div>
            <p className="text-sm text-slate-400">Современная темная тема</p>
          </button>

          <button onClick={() => onChange('system')} className={`p-4 rounded-lg border-2 transition-colors ${theme === 'system' ? 'border-primary-500 bg-primary-500/10' : 'border-border hover:border-primary-500'}`}>
            <div className="flex items-center space-x-2 mb-2">
              <Monitor size={20} />
              <span className="font-medium">Системная</span>
            </div>
            <p className="text-sm text-slate-400">Следует настройкам системы</p>
          </button>
        </div>
      </CardContent>
    </Card>
  )
}


