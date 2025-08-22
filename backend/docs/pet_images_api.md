# API изображений питомцев (БД-first)

## Обзор

API для генерации и получения уникальных визуальных изображений питомцев. Источник истины — БД: изображения хранятся в полях `image_egg_b64`, `image_baby_b64`, `image_adult_b64`. Если установлен `HF_API_TOKEN`, сервер генерирует PNG через Hugging Face; иначе используется альтернативный SVG-генератор как временный шаг до сохранения в БД.

## Эндпоинты

### GET /pet-images/{user_id}/{pet_name}

Получает изображение питомца для конкретного пользователя и имени питомца.

**Параметры:**
- `user_id` (string) - ID пользователя
- `pet_name` (string) - Имя питомца

**Ответ:**
- `200 OK` - Бинарные данные PNG (image/png)
- `404 Not Found` - Питомец не найден
- `500 Internal Server Error` - Ошибка генерации изображения

**Заголовки ответа:**
- `Cache-Control: no-cache, no-store, must-revalidate`
- `X-Pet-Stage: egg|baby|adult`
- `X-Pet-Source: db_base64|generated_and_persisted`

### GET /pet-images/{user_id}/{pet_name}/metadata

Получает метаданные изображения питомца.

**Параметры:**
- `user_id` (string) - ID пользователя
- `pet_name` (string) - Имя питомца

**Ответ:**
```json
{
  "user_id": "string",
  "pet_name": "string",
  "stage": "egg|baby|teen|adult",
  "health": 100,
  "metadata": {
    "pet_type": "cat|dog|bird|fish|rabbit|hamster|dragon|unicorn|robot|alien",
    "style": "cute|cool|mystical|sci-fi|vintage|anime|realistic|cartoon",
    "unique_features": ["особые отметины", "необычный цвет глаз"],
    "color_scheme": "excellent|good|poor|critical",
    "mood": "happy|sad|excited|sleepy|hungry|sick",
    "background": "мягкий градиентный фон"
  }
}
```

### POST /pet-images/{user_id}/regenerate

Перегенерирует все изображения питомцев пользователя.

**Параметры:**
- `user_id` (string) - ID пользователя

**Ответ:**
```json
{
  "message": "Перегенерировано 2 изображений",
  "regenerated_images": [
    {
      "pet_name": "Бобик",
      "stage": "adult",
      "health": 85,
      "image_path": "/path/to/image.png"
    }
  ]
}
```

### DELETE /pet-images/cache

Очищает весь кэш изображений питомцев.

**Ответ:**
```json
{
  "message": "Кэш изображений очищен"
}
```

## Особенности генерации

### Типы питомцев (пример)
- `cat` - Кот
- `dog` - Собака
- `bird` - Птица
- `fish` - Рыба
- `rabbit` - Кролик
- `hamster` - Хомяк
- `dragon` - Дракон
- `unicorn` - Единорог
- `robot` - Робот
- `alien` - Пришелец

### Стили питомцев
- `cute` - Милый
- `cool` - Крутой
- `mystical` - Мистический
- `sci-fi` - Научная фантастика
- `vintage` - Винтажный
- `anime` - Аниме
- `realistic` - Реалистичный
- `cartoon` - Мультяшный

### Уникальные особенности
Генерируются на основе хеша от `user_id` и `pet_name`:
- Особые отметины
- Необычный цвет глаз
- Уникальная форма ушей
- Особый хвост
- Маленькие рожки
- Крылья
- Светящиеся части
- Металлические элементы

### Цветовые схемы по здоровью
- `excellent` (80-100) - Яркие, насыщенные цвета
- `good` (50-79) - Нормальные, живые цвета
- `poor` (20-49) - Приглушенные, тусклые цвета
- `critical` (0-19) - Бледные, серые тона

### Настроения
- `happy` - Радостный, улыбающийся
- `sad` - Грустный, поникший
- `excited` - Возбужденный, энергичный
- `sleepy` - Сонный, расслабленный
- `hungry` - Голодный, с нетерпением
- `sick` - Больной, слабый

## Кэширование

Генераторы могут использовать локальную папку `cache/pet_images/` для временных файлов. Источник истины — БД. Итоговые изображения хранятся в полях таблицы `pets`.

## Обработка ошибок

- **404 Not Found** - Питомец не найден в базе данных
- **500 Internal Server Error** - Ошибка генерации изображения или проблемы с DALL-E API

## Примеры использования

### Получение изображения питомца
```bash
curl -X GET "http://localhost:3000/pet-images/user123/Бобик" \
  -H "Accept: image/png"
```

### Получение метаданных
```bash
curl -X GET "http://localhost:3000/pet-images/user123/Бобик/metadata" \
  -H "Accept: application/json"
```

### Перегенерация изображений
```bash
curl -X POST "http://localhost:3000/pet-images/user123/regenerate" \
  -H "Content-Type: application/json"
```

### Очистка кэша
```bash
curl -X DELETE "http://localhost:3000/pet-images/cache"
``` 