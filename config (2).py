TOKEN = "#" #Когда-то давно, когда программисты ещё писали код на каменных табличках,
#а баги исправляли ритуальными плясками, появился Первый API-Токен.


OWNER_ID = # # Но однажды появился Он — Первый Главный Администратор. 
# Говорят, что родился он сразу с /ban в руках, а его первым словом было "Вы не админ."




# список проектов для кнопки "Другие проекты"
projects = {
    "Test 1": "https://marginaldeveloper.github.io/Cyb3rR4tWebsite/",
    "Проект 2": "https://example.com/project2",
    "Проект 3": "https://example.com/project3"
}




from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        documents TEXT,
        photo TEXT       
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS botusers (
        tg_id INTEGER PRIMARY KEY,
        username TEXT,
        role TEXT
    )
''')
conn.commit()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        tg_id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

def get_user_role(user_id):
    if user_id == OWNER_ID:
        return "Гл. админ"
    elif is_admin(user_id):
        return "Менеджер"
    return "Пользователь"


cursor.execute("INSERT OR IGNORE INTO admins (tg_id, name) VALUES (?, ?)", (OWNER_ID, "Главный администратор"))
conn.commit()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
class Form(StatesGroup):
    adding_admin_id = State()
    adding_admin_name = State()
    deleting_admin = State()
    adding_user_name = State()
    adding_user_description = State()
    adding_user_documents = State()
    deleting_user = State()
    searching_user = State()
    chat_session = State()
    adding_user_photo = State()
    editing_user_id = State()  
    editing_user_field = State() 
    editing_user_value = State()  


global_admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Список ЧС"), KeyboardButton(text="🛠️ Список менеджеров")],
        [KeyboardButton(text="👤 Добавить В ЧС"), KeyboardButton(text="❌ Удалить из ЧС")],
        [KeyboardButton(text="🔍 Поиск пользователя"), KeyboardButton(text="🆔 Узнать свой ID")],
        [KeyboardButton(text="👥 Пользователи бота")],
        [KeyboardButton(text="📌 Другие проекты")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Список ЧС"), KeyboardButton(text="👤 Добавить В ЧС")],
        [KeyboardButton(text="❌ Удалить из ЧС"), KeyboardButton(text="🔍 Поиск пользователя")],
        [KeyboardButton(text="🆔 Узнать свой ID")],
        [KeyboardButton(text="📌 Другие проекты")]
    ],
    resize_keyboard=True
)

user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Поиск пользователя"), KeyboardButton(text="🆔 Узнать свой ID")],
        [KeyboardButton(text="📌 Другие проекты")]
    ],
    resize_keyboard=True
)

skip_photo_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📭 Пропустить")]],
    resize_keyboard=True,
    one_time_keyboard=True
)


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

def is_global_admin(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    cursor.execute("SELECT * FROM admins WHERE tg_id = ?", (user_id,))
    return cursor.fetchone() is not None

@dp.message(F.text == "✅ Добавить менеджера")
async def add_admin(message: types.Message, state: FSMContext):
    if not is_global_admin(message.from_user.id):
        return await message.answer("❌ У вас нет прав на управление менеджерами.")
    await state.set_state(Form.adding_admin_id)
    await message.answer("Введите Telegram ID нового менеджера:")

@dp.message(F.text == "📌 Другие проекты")
async def show_projects(message: Message):
    if not projects:  
        await message.answer("❌ Нет доступных проектов.")
        return
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, url=link)] for name, link in projects.items()
    ])
    

    markup.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")])

    await message.answer("📌 Наши проекты:\n\nВыберите проект, чтобы перейти:", reply_markup=markup)

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    role = get_user_role(user_id) 

    if role == "global_admin":
        keyboard = global_admin_kb
    elif role == "admin":
        keyboard = admin_kb
    else:
        keyboard = user_kb

    await callback.message.edit_text("🔙 Возвращаемся в главное меню...", reply_markup=None)
    await bot.send_message(user_id, "Выбери действие:", reply_markup=keyboard)
    await callback.answer() 

@dp.message(Form.adding_admin_id)
async def process_add_admin_id(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text)
        await state.update_data(admin_id=admin_id)
        await state.set_state(Form.adding_admin_name)
        await message.answer("Введите имя менеджера:")
    except ValueError:
        await message.answer("❌ Некорректный ID. Введите числовой Telegram ID.")

@dp.message(Form.adding_admin_name)
async def process_add_admin_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT OR IGNORE INTO admins (tg_id, name) VALUES (?, ?)", (data['admin_id'], message.text))
    conn.commit()
    await message.answer("✅ менеджер добавлен.", reply_markup=global_admin_kb)
    await state.clear()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
@dp.message(F.text == "🛠️ Список менеджеров")
async def list_admins(message: types.Message):
    cursor.execute("SELECT tg_id, name FROM admins")
    admins = cursor.fetchall()

    if admins:
        response = "🛠️ Список менеджеров:\n\n" + "\n".join([f"👤 {name} (ID: {tg_id})" for tg_id, name in admins])
    else:
        response = "❌ менеджеров нет."

    if is_global_admin(message.from_user.id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить", callback_data="add_admin")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data="delete_admin")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]
        ])
        return await message.answer(response, reply_markup=keyboard)
    
    await message.answer(response)

@dp.message(F.text == "📜 Список ЧС")
async def list_blacklist(message: types.Message, state: FSMContext):
    cursor.execute("SELECT id, name, description FROM users")
    users = cursor.fetchall()
    if not users:
        await message.answer("❌ ЧС пуст.")
        return
    await state.update_data(users=users)
    await send_blacklist_page(message, users, 0)

async def send_blacklist_page(message: types.Message, users, page):
    per_page = 5
    start = page * per_page
    end = start + per_page
    page_users = users[start:end]

    response = (
        f"📜 Список ЧС (стр. {page + 1})\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(
            [
                f"🔹 ID: {user[0]}\n"
                f"   🏷 Имя: {user[1]}\n"
                f"   📌 Описание: {user[2]}\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
                for user in page_users
            ]
        )
    )

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"blacklist_page_{page - 1}"))
    if end < len(users):
        buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"blacklist_page_{page + 1}"))
    buttons.append(InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_user"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.answer(response, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("blacklist_page_"))
async def blacklist_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = data.get("users", [])
    page = int(callback.data.split("_")[-1])
    await callback.message.edit_text("⏳ Загрузка...", reply_markup=None)
    await send_blacklist_page(callback.message, users, page)
    await callback.answer()

@dp.callback_query(F.data == "edit_user")
async def edit_user_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.editing_user_id)
    await callback.message.answer("📌 Введите ID пользователя для редактирования:")

@dp.message(Form.editing_user_id)
async def process_edit_user_id(message: types.Message, state: FSMContext):
    cursor.execute("SELECT name, description FROM users WHERE id = ?", (message.text,))
    user = cursor.fetchone()
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    await state.update_data(user_id=message.text)
    buttons = [
        InlineKeyboardButton(text="✔️ Да", callback_data="confirm_edit"),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel_edit"),
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.answer(
        f"🔹 Найден пользователь:\n🏷 Имя: {user[0]}\n📌 Описание: {user[1]}\nРедактировать?",
        reply_markup=keyboard
    )
    await state.set_state(Form.editing_user_field)

@dp.callback_query(F.data == "confirm_edit")
async def confirm_edit(callback: CallbackQuery, state: FSMContext):
    buttons = [
        InlineKeyboardButton(text="🏷 Имя", callback_data="edit_name"),
        InlineKeyboardButton(text="📌 Описание", callback_data="edit_description"),
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await callback.message.answer("📝 Выберите поле для изменения:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Отмена редактирования.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_"))
async def process_edit_user_field(callback: CallbackQuery, state: FSMContext):
    field_map = {"edit_name": "name", "edit_description": "description"}
    field = field_map.get(callback.data)
    if not field:
        await callback.answer()
        return
    await state.update_data(editing_field=field)
    await callback.message.answer("✏️ Введите новое значение:")
    await state.set_state(Form.editing_user_value)

@dp.message(Form.editing_user_value)
async def process_edit_user_value_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    field = data.get("editing_field")
    cursor.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (message.text, user_id))
    conn.commit()
    await message.answer("✅ Данные обновлены.")
    await state.clear()

@dp.callback_query(F.data == "add_admin")
async def add_admin_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.adding_admin_id)
    await call.message.answer("📝 Введите Telegram ID нового менеджера:")
    await call.answer()


@dp.callback_query(F.data == "delete_admin")
async def delete_admin_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.deleting_admin)
    await call.message.answer("🗑 Введите Telegram ID менеджера для удаления:")
    await call.answer()


@dp.callback_query(F.data == "admin_menu")
async def admin_menu_callback(call: CallbackQuery):
    await call.message.answer("🔧 Главное меню менеджера", reply_markup=global_admin_kb)
    await call.answer()


@dp.message(F.text == "❌ Удалить менеджера")
async def delete_admin(message: types.Message, state: FSMContext):
    if not is_global_admin(message.from_user.id):
        return await message.answer("❌ У вас нет прав на управление менеджерами.")
    await state.set_state(Form.deleting_admin)
    await message.answer("Введите Telegram ID менеджера для удаления:")

@dp.message(Form.deleting_admin)
async def process_delete_admin(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text)
        cursor.execute("DELETE FROM admins WHERE tg_id = ?", (admin_id,))
        conn.commit()
        await message.answer("✅ менеджер удален.", reply_markup=global_admin_kb)
        await state.clear()
    except ValueError:
        await message.answer("❌ Некорректный ID. Введите числовой Telegram ID.")

@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Неизвестный"
    role = "Пользователь"
    if is_global_admin(user_id):
        role = "Главный администратор"
        await message.answer("👑 Вы главный администратор. Выберите действие:", reply_markup=global_admin_kb)
    elif is_admin(user_id):
        role = "Менеджер"
        await message.answer("👤 Вы менеджер.", reply_markup=admin_kb)
    else:
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Я — бот, созданный для отслеживания мошенников, скаммеров и нарушителей. 🚨\n\n"
            "🔎 Вы можете ввести ФИО, документы или другие данные нарушителя, и я попробую найти информацию в базе. 😉",
            reply_markup=user_kb
        )
    
    cursor.execute("INSERT OR IGNORE INTO botusers (tg_id, username, role) VALUES (?, ?, ?)", (user_id, username, role))
    conn.commit()




@dp.message(F.text == "👤 Добавить В ЧС")
async def add_user(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ У вас нет прав на добавление пользователей.")
    await state.set_state(Form.adding_user_name)
    await message.answer("Введите имя пользователя:")

@dp.message(Form.adding_user_name)
async def process_add_user_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.adding_user_description)
    await message.answer("Введите описание пользователя:")


@dp.message(Form.adding_user_description)
async def process_add_user_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Form.adding_user_documents)
    await message.answer("Введите документы пользователя:")


@dp.message(Form.adding_user_documents)
async def process_add_user_documents(message: types.Message, state: FSMContext):
    await state.update_data(documents=message.text)
    await state.set_state(Form.adding_user_photo)
    await message.answer("📸 Отправьте фото пользователя или нажмите '📭 Пропустить'.", reply_markup=skip_photo_kb)


@dp.message(Form.adding_user_photo, F.photo)
async def process_add_user_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await save_user_to_db(state, photo_id)
    await message.answer("✅ Пользователь добавлен.", reply_markup=admin_kb)
    await state.clear()


@dp.message(Form.adding_user_photo, F.text == "📭 Пропустить")
async def process_skip_photo(message: types.Message, state: FSMContext):
    await save_user_to_db(state, photo_id=None)
    await message.answer("✅ Пользователь добавлен без фото.", reply_markup=admin_kb)
    await state.clear()


@dp.message(F.text == "❌ Отмена")
async def cancel_process(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=admin_kb)


async def save_user_to_db(state, photo_id):
    data = await state.get_data()
    cursor.execute(
        "INSERT INTO users (name, description, documents, photo) VALUES (?, ?, ?, ?)",
        (data['name'], data['description'], data['documents'], photo_id)
    )
    conn.commit()



@dp.message(F.text == "❌ Удалить из ЧС")
async def delete_user(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ У вас нет прав на удаление пользователей.")

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        return await message.answer("📭 В базе нет пользователей.")

    await state.set_state(Form.deleting_user)
    await message.answer("📌 Пожалуйста, введите ID пользователя для удаления:")

@dp.message(Form.deleting_user)
async def process_delete_user(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("⚠️ Ошибка! Введите числовой ID.")

    user_id = int(message.text)
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

    await message.answer(f"✅ Пользователь с ID {user_id} удален.")
    await state.clear()


@dp.message(Form.deleting_user)
async def process_delete_user(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        await message.answer("✅ Пользователь удален.", reply_markup=admin_kb)
        await state.clear()
    except ValueError:
        await message.answer("❌ Ошибка! Введите числовой ID.")

@dp.message(F.text == "🔍 Поиск пользователя")
async def search_user(message: types.Message, state: FSMContext):
    await state.set_state(Form.searching_user)
    await message.answer("Введите ID, имя или часть описания пользователя для поиска:")

@dp.message(Form.searching_user)
async def process_search_user(message: types.Message, state: FSMContext):
    query = f"%{message.text}%"
    cursor.execute(
        "SELECT * FROM users WHERE id = ? OR name LIKE ? OR description LIKE ?", 
        (message.text, query, query)
    )
    users = cursor.fetchall()

    if users:
        response = "🔎 Результаты поиска:\n"
        response += "━━━━━━━━━━━━━━━━━━━━━━\n"
        for user in users:
            response += (
                f"🆔 ID:{user[0]}\n"
                f"📛 Имя:{user[1]}\n"
                f"📝 Описание: {user[2]}\n"
                f"📂 Документы: {user[3]}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
            )
            if user[4]:  
                await bot.send_photo(message.chat.id, user[4])
        await message.answer(response, parse_mode="HTML")
    else:
        await message.answer("❌ Пользователь не найден.")

    await state.clear()

@dp.message(F.text == "🆔 Узнать свой ID")
async def get_user_id(message: types.Message):
    await message.answer(
    f"🌟 Ваш Telegram ID: {message.from_user.id}",
    parse_mode="HTML"
)


@dp.message(F.text == "👥 Пользователи бота")
async def list_bot_users(message: types.Message, state: FSMContext):
    if not is_global_admin(message.from_user.id):
        return await message.answer("❌ У вас нет доступа к этой команде.")
    
    cursor.execute("SELECT tg_id, username, role FROM botusers")
    users = cursor.fetchall()

    if not users:
        return await message.answer("📭 В базе нет пользователей.")

    await state.update_data(users=users)
    await send_bot_users_page(message, users, 0)


async def send_bot_users_page(message: types.Message, users, page):
    per_page = 5  # Количество пользователей на одной странице
    start = page * per_page
    end = start + per_page
    page_users = users[start:end]

    response = f"👥 <b>Пользователи бота (стр. {page + 1})</b>\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━\n"

    for tg_id, username, role in page_users:
        response += (
            f"🆔 ID: <code>{tg_id}</code>\n"
            f"👤 Ник: @{username if username else '—'}\n"
            f"🎭 Роль: {role}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"botusers_page_{page - 1}"))
    if end < len(users):
        buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"botusers_page_{page + 1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else [])
    
    await message.answer(response, parse_mode="HTML", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("botusers_page_"))
async def bot_users_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = data.get("users", [])
    page = int(callback.data.split("_")[-1])

    await callback.message.edit_text("⏳ Загрузка...", reply_markup=None)
    await send_bot_users_page(callback.message, users, page)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


