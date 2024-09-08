import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Путь к файлу, где хранится Last-Modified
file_path = "last_modified.txt"
# URL для проверки


url = "https://www.miigaik.ru/students/process/staff/Лебедев%20Евгений%20Денисович.pdf"

# Список пользователей, начавших использовать бота
users = set()

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    users.add(user_id)
    update.message.reply_text('Привет!В жизни каждого человека бывают моменты, когда зашел не в ту дверь. \nИспользуй команду /check для проверки изменений.')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def check(update: Update, context: CallbackContext) -> None:
    # Вызов функции проверки обновлений
    check_for_updates(update.message.chat_id, context)
    update.message.reply_text("Проверка изменений запущена. Если файл был изменен, вы получите уведомление.")

def check_for_updates(chat_id, context: CallbackContext):
    last_modified_server = get_last_modified_from_server()
    last_modified_file = get_last_modified_from_file()

    if last_modified_server and last_modified_server != last_modified_file:
        # Если есть изменения, обновляем файл и уведомляем пользователей
        save_last_modified_to_file(last_modified_server)
        for user_id in users:
            try:
                context.bot.send_message(chat_id=user_id, text="Файл изменен!")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

def get_last_modified_from_server():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    response = requests.get(url, headers=headers,verify=False)
    if response.status_code == 200:
        return response.headers.get('Last-Modified')
    return None

def get_last_modified_from_file():
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    return None

def save_last_modified_to_file(last_modified):
    with open(file_path, "w") as file:
        file.write(last_modified)

def job_check_for_updates(context: CallbackContext) -> None:
    check_for_updates(None, context)

def main() -> None:
    # Вставь сюда свой токен, который ты получил от BotFather
    updater = Updater()

    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check", check))

    # Обработчик текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Планируем выполнение функции проверки изменений каждый час
    job_queue.run_repeating(job_check_for_updates, interval=3600, first=0)

    # Запуск бота
    updater.start_polling()

    # Ожидание остановки бота
    updater.idle()

if __name__ == '__main__':
    main()