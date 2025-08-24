#!/usr/bin/env python3
"""
Скрипт для запуска бэкенда Telepets API
"""
import uvicorn
import sys
import os

# Добавляем путь к backend в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    # Настройка вывода в UTF-8 для Windows-консолей
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("Запуск Telepets API...")
    print("Порт: 3000")
    print("Хост: 127.0.0.1")
    print("Документация: http://127.0.0.1:3000/docs")
    print("Мониторинг: http://127.0.0.1:3000/monitoring/health")
    print("-" * 50)
    
    try:
        # Запускаем как модуль пакета backend, чтобы работали относительные импорты
        uvicorn.run(
            "backend.main:app",
            host="127.0.0.1",
            port=3000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1) 