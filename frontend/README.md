# Telepets Frontend

Современный фронтенд для игры Telepets - тамагочи для Telegram Web App.

## 🚀 Технологии

- **React 18** - Современная библиотека для создания пользовательских интерфейсов
- **TypeScript** - Типизированный JavaScript
- **Vite** - Быстрый сборщик и dev-сервер
- **Tailwind CSS** - Utility-first CSS фреймворк
- **Framer Motion** - Библиотека анимаций
- **React Query** - Управление состоянием и кэшированием
- **React Router** - Маршрутизация
- **Lucide React** - Современные иконки
- **React Hot Toast** - Уведомления

## 📱 Особенности

### 🎨 Дизайн
- **Адаптивный дизайн** - Оптимизирован для мобильных устройств и десктопа
- **Темная тема** - Современный темный интерфейс
- **Анимации** - Плавные переходы и анимации
- **Кастомные компоненты** - Переиспользуемые UI компоненты

### 🎮 Игровые функции
- **Создание питомцев** - Простой интерфейс для создания новых питомцев
- **Управление здоровьем** - Визуальные индикаторы здоровья
- **Экономика** - Система монет и покупок
- **История** - Просмотр всех питомцев и их истории
- **Детали питомца** - Подробная информация о каждом питомце

### 🔧 Технические особенности
- **TypeScript** - Полная типизация
- **React Query** - Автоматическое кэширование и обновление данных
- **Lazy Loading** - Ленивая загрузка компонентов
- **Error Boundaries** - Обработка ошибок
- **Responsive Design** - Адаптация под разные экраны

## 🛠️ Установка и запуск

### Предварительные требования
- Node.js 16+ 
- npm или yarn
- Запущенный backend API (порт 3000)

### Установка зависимостей
```bash
cd frontend
npm install
```

### Запуск в режиме разработки
```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3001

### Сборка для продакшена
```bash
npm run build
```

### Предварительный просмотр сборки
```bash
npm run preview
```

## 📁 Структура проекта

```
frontend/
├── src/
│   ├── components/          # React компоненты
│   │   ├── ui/             # Базовые UI компоненты
│   │   ├── Layout.tsx      # Главный layout
│   │   └── PetCard.tsx     # Карточка питомца
│   ├── hooks/              # Кастомные хуки
│   │   ├── usePet.ts       # Хуки для работы с питомцами
│   │   └── useEconomy.ts   # Хуки для экономики
│   ├── lib/                # Утилиты и API
│   │   ├── api.ts          # API клиент
│   │   └── utils.ts        # Утилиты
│   ├── pages/              # Страницы приложения
│   │   ├── Home.tsx        # Главная страница
│   │   ├── Economy.tsx     # Страница экономики
│   │   ├── History.tsx     # История питомцев
│   │   ├── Settings.tsx    # Настройки
│   │   └── PetDetails.tsx  # Детали питомца
│   ├── types/              # TypeScript типы
│   │   └── index.ts        # Основные типы
│   ├── App.tsx             # Главный компонент
│   ├── main.tsx            # Точка входа
│   └── index.css           # Глобальные стили
├── public/                 # Статические файлы
├── package.json            # Зависимости
├── vite.config.ts          # Конфигурация Vite
├── tailwind.config.js      # Конфигурация Tailwind
└── tsconfig.json          # Конфигурация TypeScript
```

## 🎨 Дизайн система

### Цвета
- **Primary**: Синие оттенки (#0ea5e9)
- **Background**: Темно-серый (#0f172a)
- **Surface**: Серый (#1e293b)
- **Border**: Светло-серый (#334155)
- **Health**: Зеленый/желтый/красный для здоровья
- **Coin**: Золотой (#fbbf24)

### Анимации
- **Float**: Плавающая анимация для питомцев
- **Heartbeat**: Пульсация для критического состояния
- **Wiggle**: Покачивание для интерактивных элементов

### Компоненты
- **Card**: Универсальная карточка с тенями
- **Button**: Кнопки с различными вариантами
- **LoadingSpinner**: Индикатор загрузки
- **PetCard**: Специализированная карточка питомца

## 🔌 API интеграция

### Основные endpoints
- `POST /create` - Создание питомца
- `GET /summary` - Информация о питомце
- `POST /health_up` - Увеличение здоровья
- `GET /economy/wallet/{user_id}` - Информация о кошельке
- `GET /economy/transactions/{user_id}` - История транзакций

### Автоматическое обновление
- Данные обновляются каждые 30 секунд
- React Query обеспечивает кэширование
- Оптимистичные обновления для лучшего UX

## 📱 Мобильная оптимизация

### Адаптивный дизайн
- **Mobile First** подход
- **Touch-friendly** интерфейс
- **Responsive** навигация
- **PWA** готовность

### Производительность
- **Lazy Loading** компонентов
- **Code Splitting** по маршрутам
- **Optimized Images** и анимации
- **Fast Refresh** в режиме разработки

## 🚀 Развертывание

### Vercel
```bash
npm run build
vercel --prod
```

### Netlify
```bash
npm run build
netlify deploy --prod --dir=dist
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "run", "preview"]
```

## 🔧 Конфигурация

### Переменные окружения
```env
VITE_API_URL=http://localhost:3000/api
```

### Прокси для разработки
В `vite.config.ts` настроен прокси для API:
```typescript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:3000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

## 📊 Мониторинг

### Производительность
- **Bundle Analyzer** для анализа размера бандла
- **Lighthouse** для оценки производительности
- **Core Web Vitals** мониторинг

### Ошибки
- **Error Boundaries** для отлова ошибок
- **Toast Notifications** для пользовательских уведомлений
- **Console Logging** для отладки

## 🤝 Разработка

### Code Style
- **ESLint** для линтинга
- **Prettier** для форматирования
- **TypeScript** для типизации

### Git Hooks
- **Pre-commit** проверки
- **Husky** для автоматизации

### Тестирование
- **React Testing Library** для unit тестов
- **Playwright** для e2e тестов
- **Storybook** для компонентов

## 📈 Планы развития

- [ ] **PWA** поддержка
- [ ] **Offline** режим
- [ ] **Push** уведомления
- [ ] **Social** функции
- [ ] **Achievements** система
- [ ] **Multiplayer** режим
- [ ] **Customization** питомцев
- [ ] **Mini-games** интеграция

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

---

**Telepets Frontend v1.0.0** - Современный интерфейс для тамагочи 🎮 