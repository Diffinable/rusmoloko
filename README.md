## Настройка окружения

1. Скопируй файл с примерами переменных:
   
   cp .env.example .env
   

2. При необходимости отредактируй `.env` (по умолчанию всё работает "из коробки").

3. Запусти проект:

   docker compose up -d --build
   
   docker compose exec app python seed.py
