import { useEffect, useState } from 'react';
import { isFontAvailable, getAvailableFont } from '@/lib/fonts';

interface FontLoaderProps {
  children: React.ReactNode;
}

export default function FontLoader({ children }: FontLoaderProps) {
  const [fontsLoaded, setFontsLoaded] = useState(false);
  const [fallbackApplied, setFallbackApplied] = useState(false);

  useEffect(() => {
    const checkFonts = () => {
      try {
        // Проверяем доступность основных шрифтов
        const interAvailable = isFontAvailable('Inter');
        const poppinsAvailable = isFontAvailable('Poppins');

        if (!interAvailable || !poppinsAvailable) {
          // Применяем fallback шрифты
          const root = document.documentElement;
          
          if (!interAvailable) {
            const fallbackFont = getAvailableFont('sans');
            root.style.setProperty('--font-sans', fallbackFont);
            console.log(`Применен fallback шрифт для Inter: ${fallbackFont}`);
          }
          
          if (!poppinsAvailable) {
            const fallbackFont = getAvailableFont('display');
            root.style.setProperty('--font-display', fallbackFont);
            console.log(`Применен fallback шрифт для Poppins: ${fallbackFont}`);
          }
          
          setFallbackApplied(true);
        }

        // Помечаем что шрифты проверены
        setFontsLoaded(true);
      } catch (error) {
        console.warn('Ошибка проверки шрифтов:', error);
        setFontsLoaded(true);
      }
    };

    // Проверяем сразу
    checkFonts();

    // Проверяем еще раз после загрузки страницы
    const handleLoad = () => {
      setTimeout(checkFonts, 100);
    };

    window.addEventListener('load', handleLoad);
    
    return () => {
      window.removeEventListener('load', handleLoad);
    };
  }, []);

  // Показываем загрузчик пока шрифты не проверены
  if (!fontsLoaded) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-slate-400">Загрузка шрифтов...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {children}
      {fallbackApplied && (
        <div className="fixed bottom-4 right-4 bg-yellow-600 text-white px-3 py-2 rounded-lg text-sm shadow-lg z-50">
          Используются системные шрифты
        </div>
      )}
    </>
  );
}
