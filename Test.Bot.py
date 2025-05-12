import logging
import asyncio
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.exceptions import TelegramBadRequest  # <-- Импорт обработчика ошибок
from aiogram.types import InputMediaPhoto
from datetime import datetime, timedelta, date




# Конфигурация
BOT_TOKEN = "7730531432:AAHMCTb2MC3VELVT_QQvDn6cS5wpm_s5_-4"
CHANNEL_USERNAME = "@ZHARA_barAndHookan"
ADMIN_ID = 1201484037

# FSM состояния
class AdminState(StatesGroup):
    main_menu = State()
    delete_booking = State()
    write_to_user = State()
    restore_booking = State() # Добавляем новое состояние
    confirm_delete_all = State()


class BookingState(StatesGroup):
    choosing_place = State()
    choosing_area = State()  # <--- новое состояние
    entering_name = State()
    entering_people = State()
    choosing_date = State()
    choosing_time = State()



# Инициализация базы
conn = sqlite3.connect("booking.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    people INTEGER,
    date TEXT,
    time TEXT,
    place TEXT,
    status TEXT DEFAULT 'active'
)''')
conn.commit()

# Бот и диспетчер
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Проверка подписки
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# Кнопки
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Забронировать стол", callback_data="menu_book")],
        [InlineKeyboardButton(text="📖 Мои брони", callback_data="menu_my_bookings")],
        [InlineKeyboardButton(text="ℹ️ О заведениях", callback_data="menu_about")],
        [InlineKeyboardButton(text="🤝 Сотрудничество/Поддержка", url="https://t.me/lslm_Jordan")]

    ])

def admin_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Все брони", callback_data="admin_show_bookings")],
        [InlineKeyboardButton(text="❌ Удалить бронь", callback_data="admin_delete_booking")],
        [InlineKeyboardButton(text="♻️ Восстановить бронь", callback_data="admin_restore_booking")],
        [InlineKeyboardButton(text="✉️ Написать гостю", callback_data="admin_write_to_user")],
        [InlineKeyboardButton(text="🗑 Удалить все", callback_data="admin_delete_all_bookings")],
        [InlineKeyboardButton(text="🔙 Выйти", callback_data="admin_exit")]
    ])




# Команды
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет, чем могу тебе помочь?:", reply_markup=main_menu())

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❗ Вы не админ.")
        return
    await message.answer("👨‍💻 Админ-панель:", reply_markup=admin_main_menu())
    await state.set_state(AdminState.main_menu)

# О заведении

@dp.callback_query(F.data == "menu_about")
async def show_about(call: CallbackQuery):
    # --- ЖАРА на Мясницкой ---
    await call.message.answer_media_group([
        InputMediaPhoto(media=FSInputFile("img/zharaM.webp")),
        InputMediaPhoto(media=FSInputFile("img/zharaM2.webp")),
        InputMediaPhoto(media=FSInputFile("img/zharaM3.webp"),
            caption=(
                "<b>🔥 ЖАРА на Мясницкой</b>\n"
                "📍 Москва, ул. Мясницкая, 41с3\n"
                "🕒 Вс-Чт 12:00 - 01:00, Пт-Сб 12:00 - 03:00\n"
                "🍽 Кухня, кальяны, музыка и уютная атмосфера."
            )
        )
    ])
    await call.message.answer(
        "📖 Меню:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Меню Мясницкая", callback_data="menu_food_zhara_mias")]
        ])
    )

    # --- ЖАРА на Арбате ---
    await call.message.answer_media_group([
        InputMediaPhoto(media=FSInputFile("img/zharaA1.webp")),
        InputMediaPhoto(media=FSInputFile("img/zharaA2.webp")),
        InputMediaPhoto(media=FSInputFile("img/zharaA3.webp"),
            caption=(
                "<b>🔥 ЖАРА на Арбате</b>\n"
                "📍 Москва, Новый Арбат, 21\n"
                "🕒 Пн–Чт: 12:00–01:00, Пт–Вс: 12:00–03:00\n"
                "🎶 Бар, живая музыка, танцы, кальяны."
            )
        )
    ])
    await call.message.answer(
        "📖 Меню:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Меню Арбат", callback_data="menu_food_zhara_arb")]
        ])
    )

    # --- Поклонка ---
    await call.message.answer_media_group([
        InputMediaPhoto(media=FSInputFile("img/pokl.JPG")),
        InputMediaPhoto(media=FSInputFile("img/poklFull.JPG")),
        InputMediaPhoto(media=FSInputFile("img/poklLove.JPG"),
            caption=(
                "<b>🙇 Поклонка Бар</b>\n"
                "📍 Москва, ул. Генерала Ермолова 4\n"
                "🕒 Ежедневно: 12:00 - 00:00\n"
                "🍹 Стильный бар с авторскими коктейлями, кальянами и отличной музыкой."
            )
        )
    ])
    await call.message.answer(
        "📖 Меню:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Меню Поклонка", callback_data="menu_food_poklonka")]
        ])
    )

    # --- Кнопка Назад ---
    await call.message.answer(
        "↩️ Вернуться в меню:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
    )
    await call.answer()

# Меню PDF
@dp.callback_query(F.data == "menu_food_zhara_mias")
async def show_food_zhara_mias(call: CallbackQuery):
    await call.message.answer_document(FSInputFile("files/menu_zhara_mias.pdf"), caption="📋 Меню ЖАРА на Мясницкой")
    await call.answer()

@dp.callback_query(F.data == "menu_food_zhara_arb")
async def show_food_zhara_arb(call: CallbackQuery):
    await call.message.answer_document(FSInputFile("files/menu_zhara_arb.pdf"), caption="📋 Меню ЖАРА на Арбате")
    await call.answer()

@dp.callback_query(F.data == "menu_food_poklonka")
async def show_food_poklonka(call: CallbackQuery):
    await call.message.answer_document(FSInputFile("files/menu_poklonka.pdf"), caption="📋 Меню Поклонка Бара")
    await call.message.answer_document(FSInputFile("files/menu_poklonka2.pdf"), caption="📋 Детское Меню Поклонка Бара")
    await call.answer()

# Бронирование
@dp.callback_query(F.data == "menu_my_bookings")
async def show_my_bookings(call: CallbackQuery):
    with sqlite3.connect("booking.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY status, date, time", (call.from_user.id,))
        rows = cur.fetchall()

    if not rows:
        await call.message.edit_text(
            "📭 У вас нет бронирований.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
            ])
        )
    else:
        text = "📖 Ваши бронирования:\n(🟢 - активные, 🔴 - отмененные)\n\n"
        keyboard = []

        for row in rows:
            status_icon = "🟢" if row[7] == 'active' else "🔴"
            text += (
                f"{status_icon} #{row[0]}\n"
                f"🏢 {row[6]}\n"
                f"👤 {row[2]}\n"
                f"👥 {row[3]} чел\n"
                f"📅 {row[4]} ⏰ {row[5]}\n"
                f"Статус: {'активна' if row[7] == 'active' else 'отменена'}\n\n"
            )

            # Добавляем кнопку отмены только для активных бронирований
            if row[7] == 'active':
                keyboard.append([InlineKeyboardButton(
                    text=f"❌ Отменить бронь #{row[0]}",
                    callback_data=f"cancel_booking_{row[0]}"
                )])

        # Добавляем кнопку "Назад" в конце
        keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])

        await call.message.edit_text(
            text.strip(),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )


@dp.callback_query(F.data.startswith("cancel_booking_"))
async def cancel_booking(call: CallbackQuery):
    booking_id = call.data.split("_")[2]  # Получаем ID брони

    with sqlite3.connect("booking.db") as conn:
        # Проверяем, что бронь принадлежит пользователю и активна
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='active'",
                    (booking_id, call.from_user.id))
        booking = cur.fetchone()

        if not booking:
            await call.answer("❌ Нельзя отменить эту бронь", show_alert=True)
            return

        # Помечаем бронь как отмененную
        conn.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
        conn.commit()

    # Формируем информацию о брони
    booking_info = (
        f"🏢 {booking[6]}\n"
        f"👤 {booking[2]}\n"
        f"👥 {booking[3]} чел\n"
        f"📅 {booking[4]} ⏰ {booking[5]}"
    )

    # Уведомляем пользователя
    await call.message.edit_text(
        f"❌ Бронь #{booking_id} отменена:\n\n{booking_info}\n\n"
        f"Если это произошло по ошибке, свяжитесь с администрацией.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_my_bookings")]
        ])
    )

    # Уведомляем администратора
    await bot.send_message(
        ADMIN_ID,
        f"⚠️ Пользователь отменил бронь:\n\n"
        f"#{booking_id}\n"
        f"{booking_info}\n"
        f"🆔 ID пользователя: {call.from_user.id}"
    )

    await call.answer()


@dp.callback_query(F.data.startswith("cancel_booking_"))
async def ask_confirm_cancel(call: CallbackQuery):
    booking_id = call.data.split("_")[2]

    await call.message.edit_text(
        f"❌ Вы уверены, что хотите отменить бронь #{booking_id}?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, отменить", callback_data=f"confirm_cancel_{booking_id}")],
            [InlineKeyboardButton(text="❌ Нет, вернуться назад", callback_data="menu_my_bookings")]
        ])
    )


@dp.callback_query(F.data.startswith("confirm_cancel_"))
async def confirm_cancel_booking(call: CallbackQuery):
    booking_id = call.data.split("_")[2]  # Получаем ID брони

    with sqlite3.connect("booking.db") as conn:
        # Проверяем, что бронь принадлежит пользователю и активна
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='active'",
                    (booking_id, call.from_user.id))
        booking = cur.fetchone()

        if not booking:
            await call.answer("❌ Нельзя отменить эту бронь", show_alert=True)
            return

        # Помечаем бронь как отмененную
        conn.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
        conn.commit()

    # Формируем информацию о брони
    booking_info = (
        f"🏢 {booking[6]}\n"
        f"👤 {booking[2]}\n"
        f"👥 {booking[3]} чел\n"
        f"📅 {booking[4]} ⏰ {booking[5]}"
    )

    # Уведомляем пользователя
    await call.message.edit_text(
        f"❌ Бронь #{booking_id} отменена:\n\n{booking_info}\n\n"
        f"Если это произошло по ошибке, свяжитесь с администрацией.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_my_bookings")]
        ])
    )

    # Уведомляем администратора
    await bot.send_message(
        ADMIN_ID,
        f"⚠️ Пользователь отменил бронь:\n\n"
        f"#{booking_id}\n"
        f"{booking_info}\n"
        f"🆔 ID пользователя: {call.from_user.id}"
    )

    await call.answer()

@dp.callback_query(F.data == "menu_book")
async def choose_place(call: CallbackQuery, state: FSMContext):
    if not await is_subscribed(call.from_user.id):
        await call.message.edit_text(f"❗ Подпишитесь на канал: {CHANNEL_USERNAME}")
        return
    await call.message.edit_text("🏢 Выберите заведение:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 ЖАРА на Мясницкой", callback_data="place_zhara_mias")],
        [InlineKeyboardButton(text="🔥 ЖАРА на Арбате", callback_data="place_zhara_arb")],
        [InlineKeyboardButton(text="🙇 Поклонка бар(до 01.06 бронирования не работают)", callback_data="place_poklonka")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ]))
    await state.set_state(BookingState.choosing_place)

@dp.callback_query(F.data == "back_main")
async def back_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("👋 Главное меню:", reply_markup=main_menu())

@dp.callback_query(F.data.startswith("place_"))
async def choose_area_or_enter_name(call: CallbackQuery, state: FSMContext):
    if not await is_subscribed(call.from_user.id):
        await call.message.edit_text(f"❗ Подпишитесь на канал: {CHANNEL_USERNAME}")
        return

    # Проверка для Поклонки
    if call.data == "place_poklonka":
        today = datetime.now().date()
        if today < date(2024, 6, 1):  # Проверяем, что текущая дата раньше 1 июня
            await call.message.edit_text(
                "🙇 Поклонка бар откроется 1 июня 2024 года.\n"
                "Бронирование будет доступно с этой даты.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_book")]
                ])
            )
            return

    if call.data == "place_zhara_mias":
        await state.update_data(place="🔥 ЖАРА на Мясницкой")
        await call.message.edit_text("💺 Выберите тип зала:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🥂 VIP-комната", callback_data="area_vip")],
            [InlineKeyboardButton(text="🪑 Общий зал", callback_data="area_common")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_book")]
        ]))
        await state.set_state(BookingState.choosing_area)
    else:
        places = {
            "place_zhara_arb": "🔥 ЖАРА на Арбате",
            "place_poklonka": "🙇 Поклонка бар"
        }
        await state.update_data(place=places[call.data], area=None)
        await call.message.edit_text("👤 Введите ваше имя:")
        await state.set_state(BookingState.entering_name)

@dp.callback_query(F.data.in_({"area_vip", "area_common"}))
async def handle_area_choice(call: CallbackQuery, state: FSMContext):
    if call.data == "area_vip":
        await state.update_data(area="VIP-комната")
        await call.message.edit_text("💎 Вы выбрали VIP-комнату.\n💰 Депозит: 3000 ₽\n👥 До 8 человек.\n\n👤 Введите ваше имя:")
    else:
        await state.update_data(area="Общий зал")
        await call.message.edit_text("👥 Вы выбрали общий зал.\n\n👤 Введите ваше имя:")
    await state.set_state(BookingState.entering_name)

@dp.message(BookingState.entering_name)
async def enter_people(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("👥 Сколько человек?")
    await state.set_state(BookingState.entering_people)


@dp.message(BookingState.entering_people)
async def choose_date(message: Message, state: FSMContext):
    try:
        people = int(message.text.strip())
        data = await state.get_data()

        if data.get("area") == "VIP-комната" and people > 8:
            await message.answer("⚠️ В VIP-комнате максимум 8 человек. Введите корректное количество гостей.")
            return

        await state.update_data(people=people)
        today = datetime.now()

        # Для Поклонки показываем даты только с 1 июня
        if data.get("place") == "🙇 Поклонка бар":
            start_date = date(2024, 6, 1)
            if today.date() < start_date:
                available_dates = [start_date + timedelta(days=i) for i in range(3)]
            else:
                available_dates = [today.date() + timedelta(days=i) for i in range(3)]
        else:
            available_dates = [today.date() + timedelta(days=i) for i in range(3)]

        kb = [[InlineKeyboardButton(text=d.strftime("%d.%m.%Y"),
                                    callback_data=f"date_{d.strftime('%Y-%m-%d')}")]
              for d in available_dates]
        kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="menu_book")])

        await message.answer("📅 Выберите дату:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        await state.set_state(BookingState.choosing_date)
    except:
        await message.answer("⚠️ Введите число.")

@dp.callback_query(F.data.startswith("date_"))
async def choose_time(call: CallbackQuery, state: FSMContext):
    await state.update_data(date=call.data.split("_")[1])
    times = [f"{h:02d}:{m:02d}" for h in range(12, 24) for m in (0, 30)]
    kb = [[InlineKeyboardButton(text=t, callback_data=f"time_{t}")] for t in times]
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="menu_book")])
    await call.message.edit_text("⏰ Выберите время:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(BookingState.choosing_time)

@dp.callback_query(F.data.startswith("time_"))
async def save_booking(call: CallbackQuery, state: FSMContext):
    try:
        time = call.data.split("_")[1]
        await state.update_data(time=time)
        data = await state.get_data()

        # Формируем финальный текст
        place = data.get("place")
        area = data.get("area")
        full_place = f"{place} - {area}" if area else place

        # Сохраняем бронь
        with sqlite3.connect("booking.db") as conn:
            cur = conn.cursor()
            cur.execute('''INSERT INTO bookings (user_id, name, people, date, time, place)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (call.from_user.id, data['name'], data['people'], data['date'], data['time'], full_place))
            conn.commit()

        # Уведомление пользователю
        await call.message.edit_text(
            f"✅ Бронь подтверждена!\n\n"
            f"🏢 <b>{full_place}</b>\n"
            f"👤 <b>{data['name']}</b>\n"
            f"👥 <b>{data['people']} человек</b>\n"
            f"📅 <b>{data['date']}</b>\n"
            f"⏰ <b>{data['time']}</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_main")]
            ])
        )

        # Уведомление админу
        await bot.send_message(
            ADMIN_ID,
            f"📢 Новая бронь:\n"
            f"🏢 {full_place}\n"
            f"👤 {data['name']}\n"
            f"👥 {data['people']} человек\n"
            f"📅 {data['date']} ⏰ {data['time']}\n"
            f"🆔 ID: {call.from_user.id}"
        )

        await state.clear()

    except TelegramBadRequest:
        await call.message.answer("❗ Ошибка отображения сообщения. Возможно, сообщение слишком старое.")

# Восстановление брони
@dp.callback_query(F.data == "admin_restore_booking")
async def admin_restore_request(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("✏️ Введите ID отмененной брони для восстановления:")
    await state.set_state(AdminState.restore_booking)


@dp.message(AdminState.restore_booking)
async def admin_restore_confirm(message: Message, state: FSMContext):
    try:
        booking_id = int(message.text.strip())
        with sqlite3.connect("booking.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id, place, date, time, status FROM bookings WHERE id=?", (booking_id,))
            booking = cur.fetchone()

            if not booking:
                await message.answer("⚠️ Бронь с таким ID не найдена.")
                return

            user_id, place, date, time, status = booking

            if status == 'active':
                await message.answer("⚠️ Эта бронь уже активна.")
                return

            conn.execute("UPDATE bookings SET status='active' WHERE id=?", (booking_id,))
            conn.commit()

            try:
                await bot.send_message(
                    user_id,
                    f"✅ Ваша бронь восстановлена:\n\n"
                    f"🏢 {place}\n"
                    f"📅 {date} ⏰ {time}\n\n"
                    f"Приносим извинения за временные неудобства."
                )
                await message.answer(f"✅ Бронь #{booking_id} восстановлена. Пользователь уведомлен.")
            except TelegramBadRequest:
                await message.answer(f"✅ Бронь #{booking_id} восстановлена, но не удалось уведомить пользователя.")

    except ValueError:
        await message.answer("⚠️ Некорректный ID.")

    await message.answer("🔙 Назад в админ-панель:", reply_markup=admin_main_menu())
    await state.set_state(AdminState.main_menu)
# Админ-панель
@dp.callback_query(F.data == "admin_show_bookings")
async def admin_all(call: CallbackQuery):
    with sqlite3.connect("booking.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings ORDER BY status, date, time")
        rows = cur.fetchall()

    if not rows:
        await call.message.edit_text("📭 Нет бронирований.")
    else:
        text = "📖 Все бронирования:\n(🟢 - активные, 🔴 - отмененные)\n\n"
        for row in rows:
            status_icon = "🟢" if row[7] == 'active' else "🔴"
            text += (
                f"{status_icon} #{row[0]}\n"
                f"🏢 {row[6]}\n"
                f"👤 {row[2]}\n"
                f"👥 {row[3]}\n"
                f"📅 {row[4]} ⏰ {row[5]}\n"
                f"🆔 {row[1]}\n"
                f"Статус: {'активна' if row[7] == 'active' else 'отменена'}\n\n"
            )

        # Разбиваем на несколько сообщений, если слишком длинное
        messages = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for msg in messages:
            await call.message.answer(msg)

@dp.callback_query(F.data == "admin_delete_booking")
async def admin_del_request(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("✏️ Введите ID брони для удаления:")
    await state.set_state(AdminState.delete_booking)


@dp.message(AdminState.delete_booking)
async def admin_del_confirm(message: Message, state: FSMContext):
    try:
        booking_id = int(message.text.strip())
        with sqlite3.connect("booking.db") as conn:
            # Получаем данные брони перед обновлением
            cur = conn.cursor()
            cur.execute("SELECT user_id, place, date, time FROM bookings WHERE id=?", (booking_id,))
            booking = cur.fetchone()

            if booking:
                user_id, place, date, time = booking
                # Помечаем бронь как отмененную вместо удаления
                conn.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
                conn.commit()

                # Отправляем уведомление пользователю
                try:
                    await bot.send_message(
                        user_id,
                        f"❗ Ваша бронь отменена админом:\n\n"
                        f"🏢 {place}\n"
                        f"📅 {date} ⏰ {time}\n\n"
                        f"По всем вопросам обращайтесь к поддержке."
                    )
                    await message.answer("✅ Бронь отменена. Пользователь уведомлен.")
                except TelegramBadRequest:
                    await message.answer(
                        "✅ Бронь отменена, но не удалось уведомить пользователя (возможно, он заблокировал бота).")
            else:
                await message.answer("⚠️ Бронь с таким ID не найдена.")
    except ValueError:
        await message.answer("⚠️ Некорректный ID.")

    await message.answer("🔙 Назад в админ-панель:", reply_markup=admin_main_menu())
    await state.set_state(AdminState.main_menu)

@dp.callback_query(F.data == "admin_write_to_user")
async def write_to_user_start(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите ID пользователя и сообщение:\nПример: 1234567890 Привет!")
    await state.set_state(AdminState.write_to_user)

@dp.message(AdminState.write_to_user)
async def write_message_user(message: Message, state: FSMContext):
    try:
        parts = message.text.split(maxsplit=1)
        user_id = int(parts[0])
        msg_text = parts[1] if len(parts) > 1 else "Привет!"
        try:
            await bot.send_message(user_id, msg_text)
            await message.answer("✅ Сообщение отправлено.")
        except TelegramBadRequest:
            await message.answer("⚠️ Ошибка: пользователь не доступен или заблокировал бота.")
    except:
        await message.answer("⚠️ Неверный формат.")
    await message.answer("🔙 Админ-панель:", reply_markup=admin_main_menu())
    await state.set_state(AdminState.main_menu)


@dp.callback_query(F.data == "admin_delete_all_bookings")
async def delete_all(call: CallbackQuery):
    with sqlite3.connect("booking.db") as conn:
        # Получаем все активные брони перед обновлением
        cur = conn.cursor()
        cur.execute("SELECT user_id, place, date, time FROM bookings WHERE status='active'")
        active_bookings = cur.fetchall()

        # Помечаем все брони как отмененные
        conn.execute("UPDATE bookings SET status='cancelled' WHERE status='active'")
        conn.commit()



    # Уведомляем всех пользователей
    notified = 0
    for user_id, place, date, time in active_bookings:
        try:
            await bot.send_message(
                user_id,
                f"❗ Ваша бронь отменена админом:\n\n"
                f"🏢 {place}\n"
                f"📅 {date} ⏰ {time}\n\n"
                f"По всем вопросам обращайтесь к поддержке."
            )
            notified += 1
        except TelegramBadRequest:
            continue

    await call.message.edit_text(
        f"✅ Все брони отменены. Уведомлено {notified}/{len(active_bookings)} пользователей.",
        reply_markup=admin_main_menu()
    )

@dp.callback_query(F.data == "admin_exit")
async def admin_exit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🚪 Вышли из админ-панели.", reply_markup=main_menu())

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
