
Установка переводов
pybabel extract .\film_bot\ -o .\film_bot\apps\bot\locales\film_bot.pot
pybabel init -i .\film_bot\apps\bot\locales\film_bot.pot -d .\film_bot\apps\bot\locales\ -D film_bot -l ru
pybabel init -i .\film_bot\apps\bot\locales\film_bot.pot -d .\film_bot\apps\bot\locales\ -D film_bot -l en
pybabel init -i .\film_bot\apps\bot\locales\film_bot.pot -d .\film_bot\apps\bot\locales\ -D film_bot -l kz

1. Вытаскиваем тексты из файлов, Добавляем текст в переведенные версии

# Обновить переводы

pybabel extract .\film_bot\apps\ -o .\film_bot\apps\bot\locales\film_bot.pot
pybabel update -d .\film_bot\apps\bot\locales -D film_bot -i .\film_bot\apps\bot\locales\film_bot.pot

# После перевода

pybabel compile -d .\film_bot\apps\bot\locales\ -D film_bot

Запуск бота: poetry run python film_bot\main.py

