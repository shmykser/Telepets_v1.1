import { useQuery, useMutation, useQueryClient } from 'react-query'
import { userProfileApi } from '@/lib/api'
import type { UpdateProfileRequest } from '@/types'
import { notifySuccess, notifyError } from '@/components/Notification'

// Хук для получения профиля пользователя
export const useUserProfile = () => {
  return useQuery({
    queryKey: ['userProfile'],
    queryFn: userProfileApi.getProfile,
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 2,
  })
}

// Хук для обновления профиля пользователя
export const useUpdateProfile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: UpdateProfileRequest) => userProfileApi.updateProfile(data),
    onSuccess: (data) => {
      // Обновляем кэш профиля
      queryClient.setQueryData(['userProfile'], data)
      
      // Инвалидируем связанные запросы
      queryClient.invalidateQueries(['userProfile'])
      
      notifySuccess('Профиль успешно обновлен')
    },
    onError: (error: any) => {
      // Pydantic ошибки приходят в формате { detail: [{ msg, ... }] }
      const d = error?.response?.data?.detail
      const message = Array.isArray(d) ? (d[0]?.msg || 'Ошибка обновления профиля') : (d || 'Ошибка обновления профиля')
      notifyError(typeof message === 'string' ? message : 'Ошибка обновления профиля')
    },
  })
}

// Хук для получения публичной информации о пользователе
export const usePublicUserInfo = (userId: string) => {
  return useQuery({
    queryKey: ['publicUserInfo', userId],
    queryFn: () => userProfileApi.getPublicInfo(userId),
    staleTime: 10 * 60 * 1000, // 10 минут
    retry: 2,
    enabled: !!userId,
  })
}
