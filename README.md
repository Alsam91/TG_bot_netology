# Курсовая работа для онлайн-школы "Нетология"
## Телеграмм-бот для изучения английского языка. Версия 2.
Перед первым запуском бота необходимо выполнить по-порядку следующие действия:
1. Создать файл "config.ini" содержащий конфигурацию для подключения к БД и Telegram-токен. Шаблон:
    ```
    [dbaccess]
    dbname=tg_bot_db    # имя БД не менять!
    user=               # имя пользователя
    password=           # пароль
    host=               # имя хоста
    port=               # номер порта
    
    [tg]
    token=              # Telegram-токен
    ```
2. Запустить файл "create_db.py". После чего будет создана БД со следующей схемой:
![Схема БД](tg_bot_db%20-%20public.png)
   * Таблица "users" - хранит информацию о пользователях
   * Таблица "words" - хранит слова и их переводы
   * Таблица "users_words" - слова и переводы, которые добавили пользователи с привязкой к Telegram-ID этих пользователей

Для начала учёбы нужно отправить боту сообщения "/start" или "/cards"\
Можно добавлять новые слова, они будут доступны только для того пользователя, который их добавил.\
Можно удалять добавленные пользователем слова.
