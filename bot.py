import asyncio
from telegram import Bot, InputFile, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram.constants import ParseMode

TOKEN = "7644650564:AAHPtYEgWEnEekmlHK6_DHtI8_zfY0Qg7KQ"
bot = Bot(token=TOKEN)

# Состояния диалога
CHOOSING_ROLE, GET_PHONE = range(2)

# Меню для разных ролей
seller_menu = ReplyKeyboardMarkup(
    [
        ["✅ Чек-лист менеджера","🎧 Аудио инструкция"],
        ["🎥 Видеоинструкция работе на платформе"],
        ["📚 Инструкция по бронированию в сервисе"]
    ],
    resize_keyboard=True
)

driver_menu = ReplyKeyboardMarkup(
    [
        ["📚 Инструкция для водителя"],
        ["📄 Тарифы за поездки"],
    ],
    resize_keyboard=True
)

# Тексты для разных ролей
SELLER_TEXT = [
    """<b>✨ Инструкция для менеджеров по продажам inTrips ✨</b>

🌴 <i>В связи с ограничением на работу пляжей по г. Анапа и Анапскому району, на сегодняшний день не представляется возможность организовывать точки продаж на пляжах.</i>

🎉 <b>Добро пожаловать в команду inTrips!</b>
Эта подробная инструкция поможет вам:
- Эффективно искать клиентов
- Вести диалог
- Помогать в выборе экскурсий
- Справляться с возражениями
- Правильно оформлять бронирование""",

"""<b>1. Где искать потенциальных клиентов</b>

<b>1.1 Онлайн-источники</b> 🌐
- Социальные сети: ВКонтакте, Instagram, Одноклассники
- Тематические группы и форумы
- Мессенджеры: WhatsApp, Telegram
- Таргетированная реклама
- Партнерские сайты и блоги
- Мониторинг комментариев:
  <i>Пример ответа:</i>
  "Здравствуйте! Благодарим за интерес. Подскажите, какой тип отдыха вас интересует: активный, семейный, морской?""",

        """<b>1.2 Офлайн-источники</b> 🏢
- Туристические информационные центры
- Стойки с билетами
- Отели/хостелы (размещение материалов)""",

        """<b>2. Этапы общения с клиентом</b>

<b>2.1 Установление контакта</b> 🤝
<i>Пример:</i>
"Здравствуйте, меня зовут [Имя], я менеджер компании inTrips."

<b>2.2 Выявление потребностей</b> ❓
Вопросы:
- Какие у вас планы?
- Путешествуете один или с семьей?
- Какие виды экскурсий интересуют?""",

        """<b>3. Помощь в выборе экскурсии</b>

<b>3.1 Презентация экскурсии</b> 🎯
Метод FAB:
- Особенности → Преимущества → Польза
<i>Пример:</i>
"Этот тур включает посещение Кипарисового озера. Вы сможете сделать уникальные фото.""",

        """<b>4. Работа с возражениями</b> 🙌
<i>Возражение:</i> "Цена слишком высокая"
<i>Ответ:</i> "Предлагаем лучший баланс цены и качества"

<b>5. Оформление бронирования</b> 📝
1. Выберите экскурсию → дату → количество человек
2. Введите данные клиента
3. Отправьте QR-код бота @intrips_bot""",

        """<b>6. Итоговая рекомендация</b> 👉
- Быстро реагируйте на обращения
- Используйте персонализированный подход
- Следуйте инструкциям

<i>Каждый клиент должен получить незабываемый опыт!</i>

© inTrips, 2025. Для внутреннего использования.
Обновлено: 20.04.2025"""
]

DRIVER_TEXT = [
    """<b>🚕 Инструкция для водителей inTrips ✨</b>

🌍 <i>Добро пожаловать в команду профессиональных водителей!</i>

Основные правила:
- Всегда проверяйте техническое состояние автомобиля
- Соблюдайте график подачи транспорта
- Поддерживайте чистоту в салоне""",

    """<b>1. Безопасность движения</b>

    🔧 Обязательные проверки:
    - Уровень масла и технических жидкостей
    - Давление в шинах
    - Работа тормозной системы
    - Наличие аптечки и огнетушителя""",
    """<b>2. Взаимодействие с клиентами</b>

🤝 Правила общения:
- Приветствуйте пассажиров при посадке
- Помогайте с багажом
- Соблюдайте маршрут поездки
- Отвечайте на вопросы вежливо""",
    """<b>3. Тарифы и оплата</b>

💰 Актуальные расценки:
- Указаны в тарифах

© inTrips, 2025. Для внутреннего использования."""
]

def save_to_file(user_data: dict, phone: str):
    with open("users_data.txt", "a", encoding="utf-8") as f:
        f.write(
            f"ID: {user_data['user_id']}, "
            f"Имя: {user_data['first_name']}, "
            f"Телефон: {phone}, "
            f"Роль: {user_data['role']}\n"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data.update({
        'user_id': user.id,
        'first_name': user.first_name,
        'role': None
    })

    await update.message.reply_text(
        "Приветствуем на обучающей платформе компании inTrips!\n"
        "Выберите вашу роль:",
        reply_markup=ReplyKeyboardMarkup(
            [["🚕 Водитель", "👔 Менеджер по продажам"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return CHOOSING_ROLE

async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text
    context.user_data['role'] = role

    await update.message.reply_text(
        "Пожалуйста, поделитесь своим номером телефона:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Поделиться номером", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    save_to_file(context.user_data, phone)

    menu = seller_menu if context.user_data['role'] == "👔 Менеджер по продажам" else driver_menu
    role_name = "менеджер" if context.user_data['role'] == "👔 Менеджер по продажам" else "водитель"

    # Отправляем приветствие
    await update.message.reply_text(
        f"Спасибо! Добро пожаловать на обучающую платформу компании inTrips, {role_name}!",
        reply_markup=menu
    )

    # Запускаем отложенную отправку сообщений
    asyncio.create_task(send_auto_messages(update, context))

    # Запускаем отложенное сообщение через 2 минуты
    asyncio.create_task(send_registration_message(update, context))

    return ConversationHandler.END

async def send_registration_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(120)  # 2 минуты = 120 секунд
    try:
        await update.message.reply_text(
            "Перейдите по ссылке для регистрации на платформе в качестве продавца: "
            "https://intrips.online и отправьте свой логин и пароль на адрес "
            "@intrips_go с указанием Ф.И.О., номера телефона и года рождения",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Ошибка отправки регистрационного сообщения: {e}")

async def send_auto_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(3)
    role = context.user_data['role']
    texts = SELLER_TEXT if role == "👔 Менеджер по продажам" else DRIVER_TEXT

    for text in texts:
        try:
            await update.message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    role = context.user_data.get('role', '')

    try:
        if "📚 Инструкция" in text:
            await send_instruction(update, role)
        elif "🎥 Видеоинструкция" in text:
            await send_video(update, role)
        elif "📄 PDF" in text:
            await send_pdf(update, role)
        elif "🎧 Аудио" in text:
            await send_audio(update, role)
        elif "✅ Чек-лист" in text:
            await send_checklist(update, role)
        elif "📄 Тарифы" in text:
            await send_tariffs(update)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def send_instruction(update: Update, role: str):
    file_type = "seller" if "Менеджер" in role else "driver"
    with open(f"media/{file_type}_instruction.pdf", "rb") as f:
        await update.message.reply_document(f)

async def send_video(update: Update, role: str):
    file_type = "seller" if "Менеджер" in role else "driver"
    with open(f"media/{file_type}_video.mp4", "rb") as f:
        await update.message.reply_video(f)

async def send_pdf(update: Update, role: str):
    file_type = "seller" if "Менеджер" in role else "driver"
    with open(f"media/{file_type}_manual.pdf", "rb") as f:
        await update.message.reply_document(f)

async def send_audio(update: Update, role: str):
    file_type = "seller" if "Менеджер" in role else "driver"
    with open(f"media/{file_type}_audio.mp3", "rb") as f:
        await update.message.reply_audio(f)

async def send_checklist(update: Update, role: str):
    file_type = "seller" if "Менеджер" in role else "driver"
    with open(f"media/{file_type}_checklist.pdf", "rb") as f:
        await update.message.reply_document(f)

async def send_tariffs(update: Update):
    with open("media/tariffs.pdf", "rb") as f:
        await update.message.reply_document(f)

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
            GET_PHONE: [
                MessageHandler(filters.CONTACT | filters.TEXT, get_phone)
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    application.run_polling()