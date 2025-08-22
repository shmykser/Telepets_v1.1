import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Switch } from '@/components/ui/Switch'
import { useUserProfile, useUpdateProfile } from '@/hooks/useUserProfile'
import { User, Save, X } from 'lucide-react'

export default function ProfileSettings() {
  const { data: profile, isLoading, error } = useUserProfile()
  const { mutate: updateProfile, isPending } = useUpdateProfile()
  
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [displayName, setDisplayName] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [tempIsAnonymous, setTempIsAnonymous] = useState(false)
  const [tempDisplayName, setTempDisplayName] = useState('')

  // Инициализация состояния из профиля
  useEffect(() => {
    if (profile) {
      setIsAnonymous(profile.is_anonymous)
      setDisplayName(profile.display_name || '')
      setTempIsAnonymous(profile.is_anonymous)
      setTempDisplayName(profile.display_name || '')
    }
  }, [profile])

  const handleEdit = () => {
    setIsEditing(true)
    setTempIsAnonymous(isAnonymous)
    setTempDisplayName(displayName)
  }

  const handleCancel = () => {
    setIsEditing(false)
    setTempIsAnonymous(isAnonymous)
    setTempDisplayName(displayName)
  }

  const handleSave = () => {
    const updateData: any = {}
    
    if (tempIsAnonymous !== isAnonymous) {
      updateData.is_anonymous = tempIsAnonymous
    }
    
    if (tempDisplayName !== displayName) {
      const trimmed = (tempDisplayName || '').trim()
      // Пустую строку не отправляем — либо опускаем поле, либо явно ставим null (сброс)
      updateData.display_name = trimmed.length > 0 ? trimmed : null
    }
    
    if (Object.keys(updateData).length > 0) {
      updateProfile(updateData, {
        onSuccess: () => {
          setIsEditing(false)
          setIsAnonymous(tempIsAnonymous)
          setDisplayName(tempDisplayName)
        }
      })
    } else {
      setIsEditing(false)
    }
  }

  const handleAnonymousToggle = (checked: boolean) => {
    setTempIsAnonymous(checked)
    if (!checked) {
      setTempDisplayName('')
    } else {
      // При включении анонимности, если поле пустое — подставим текущее имя
      const fallback = displayName || profile?.telegram_username || (profile as any)?.username || ''
      if (!(tempDisplayName || '').trim() && fallback) {
        setTempDisplayName(fallback)
      }
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-slate-500">Загрузка профиля...</div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-red-500">
            Ошибка загрузки профиля: {error.message}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!profile) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-red-500">Профиль не найден</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <User size={20} />
          <span>Настройки профиля</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Текущий профиль */}
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700">Текущее имя</label>
            <div className="mt-1 text-lg font-semibold">
              {profile.public_name}
              {profile.is_anonymous && (
                <span className="ml-2 text-xs text-slate-500">(анонимно)</span>
              )}
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium text-slate-700">Telegram username</label>
            <div className="mt-1 text-slate-600">
              {profile.telegram_username || 'Не указан'}
            </div>
          </div>
        </div>

        {/* Настройки анонимности */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-slate-700">Анонимность</label>
              <div className="text-xs text-slate-500 mt-1">
                {isAnonymous ? 'Скрыть реальное имя' : 'Показывать реальное имя'}
              </div>
            </div>
            <Switch
              checked={isEditing ? tempIsAnonymous : isAnonymous}
              onCheckedChange={isEditing ? handleAnonymousToggle : undefined}
              disabled={!isEditing}
            />
          </div>

          {isEditing && tempIsAnonymous && (
            <div>
              <label className="text-sm font-medium text-slate-700">
                Имя для отображения
              </label>
              <div className="text-xs text-slate-500 mb-2">
                Другие игроки будут видеть это имя вместо вашего username
              </div>
              <Input
                value={tempDisplayName}
                onChange={(e) => setTempDisplayName((e.target as HTMLInputElement).value)}
                placeholder="Введите имя для отображения"
                maxLength={20}
                className="w-full"
              />
              <div className="text-xs text-slate-500 mt-1">
                {tempDisplayName.length}/20 символов
              </div>
            </div>
          )}

          {/* Предпросмотр */}
          {isEditing && (
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="text-sm font-medium text-slate-700 mb-2">Предпросмотр:</div>
              <div className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {tempIsAnonymous && (tempDisplayName || '').trim() ? tempDisplayName : 
                 tempIsAnonymous ? 'Анонимный игрок' : 
                 profile.telegram_username || profile.username || 'Неизвестный игрок'}
              </div>
              {tempIsAnonymous && (
                <div className="text-xs text-slate-500 mt-1">
                  {tempDisplayName ? 'Другие игроки увидят это имя' : 'Укажите имя для отображения'}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Кнопки управления */}
        <div className="flex space-x-3">
          {!isEditing ? (
            <Button onClick={handleEdit} variant="outline" className="flex-1">
              Редактировать
            </Button>
          ) : (
            <>
              <Button 
                onClick={handleCancel} 
                variant="outline" 
                className="flex-1"
                disabled={isPending}
              >
                <X size={16} className="mr-2" />
                Отмена
              </Button>
              <Button 
                onClick={handleSave} 
                className="flex-1"
                disabled={isPending || (tempIsAnonymous && !tempDisplayName.trim())}
              >
                <Save size={16} className="mr-2" />
                {isPending ? 'Сохранение...' : 'Сохранить'}
              </Button>
            </>
          )}
        </div>

        {/* Информация */}
        <div className="text-xs text-slate-500 space-y-1">
          <div>• При включении анонимности необходимо указать отображаемое имя</div>
          <div>• Имя должно содержать от 2 до 20 символов</div>
          <div>• Допустимы буквы, цифры, пробелы, дефисы и подчеркивания</div>
        </div>
      </CardContent>
    </Card>
  )
}
