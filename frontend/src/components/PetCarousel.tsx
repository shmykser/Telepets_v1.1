import useEmblaCarousel from 'embla-carousel-react'
import { useEffect, useCallback, useMemo } from 'react'
import PetCard from '@/components/PetCard'
import type { Pet } from '@/types'
import { getStoredUserId } from '@/utils'

interface PetCarouselProps {
  pets: Pet[]
  onSelect?: (petName: string) => void
  onHealthUp: (petName?: string) => void
  onHealthUpWithCost: (petName?: string) => void
  onResurrect?: (petName: string) => void
  isHealthUpLoading?: boolean
  isHealthUpWithCostLoading?: boolean
  walletCoins?: number
  actionCosts?: { resurrect?: number; health_up?: { egg: number; baby: number; adult: number } }
}

export default function PetCarousel({
  pets,
  onSelect,
  onHealthUp,
  onHealthUpWithCost,
  onResurrect,
  isHealthUpLoading,
  isHealthUpWithCostLoading,
  walletCoins,
  actionCosts,
}: PetCarouselProps) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: false, skipSnaps: false, align: 'center' })
  const userId = useMemo(() => getStoredUserId(), [])

  // Готовим данные: если нет image_url, подставляем URL генерации по userId и текущей стадии
  const normalizedPets: Pet[] = useMemo(() => (
    pets.map(p => ({
      ...p,
      image_url: p.image_url || `/pet-images/${userId}/${encodeURIComponent(p.name || '')}?stage=${p.state}`,
    }))
  ), [pets, userId])

  // Сортировка: сначала живые (alive/dying/не dead), затем мёртвые, внутри групп по created_at (старые раньше)
  const sortedPets: Pet[] = useMemo(() => {
    const toTime = (value?: string) => {
      const t = value ? Date.parse(value) : NaN
      return Number.isNaN(t) ? 0 : t
    }
    const isDead = (p: Pet) => p.status === 'dead' || p.life_status === 'dead'
    return [...normalizedPets].sort((a, b) => {
      const deadA = isDead(a)
      const deadB = isDead(b)
      if (deadA !== deadB) return deadA ? 1 : -1
      const ta = toTime(a.created_at)
      const tb = toTime(b.created_at)
      // Новые раньше старых (по убыванию времени создания)
      return tb - ta
    })
  }, [normalizedPets])

  const onSelectSlide = useCallback(() => {
    if (!emblaApi || !onSelect) return
    const index = emblaApi.selectedScrollSnap()
    const pet = sortedPets[index]
    if (pet?.name) onSelect(pet.name)
  }, [emblaApi, onSelect, sortedPets])

  useEffect(() => {
    if (!emblaApi) return
    emblaApi.on('select', onSelectSlide)
  }, [emblaApi, onSelectSlide])

  return (
    <div className="embla">
      <div className="embla__viewport" ref={emblaRef}>
        <div className="embla__container">
          {sortedPets.map((pet) => (
            <div className="embla__slide" key={pet.id || pet.name}>
              <PetCard
                pet={pet}
                onHealthUp={() => onHealthUp(pet.name)}
                onHealthUpWithCost={() => onHealthUpWithCost(pet.name)}
                onResurrect={onResurrect ? () => onResurrect(pet.name || '') : undefined}
                isHealthUpLoading={Boolean(isHealthUpLoading)}
                isHealthUpWithCostLoading={Boolean(isHealthUpWithCostLoading)}
                showCost
                walletCoins={walletCoins}
                resurrectCost={actionCosts?.resurrect}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}


