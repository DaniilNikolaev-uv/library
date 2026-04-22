FROM oven/bun:1-slim

WORKDIR /app

# Копируем только package.json (и lock, если он всё же есть)
# Использование * позволяет Docker не падать, если файла bun.lockb нет
COPY package.json bun.lockb* ./

# Устанавливаем зависимости
RUN bun install

# Копируем исходный код
COPY . .

# Сборка Next.js (создает папку .next)
RUN bun run build

# Next.js по умолчанию работает на 3000 порту
EXPOSE 3000

# Запуск в режиме продакшена
CMD ["bun", "run", "start"]
