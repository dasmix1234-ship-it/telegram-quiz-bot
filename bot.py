import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Твой актуальный токен и ID
BOT_TOKEN = "8223693755:AAH-cCy7_kzwtf_E1oMiyBsH7pfZi7yU_UU"
ADMIN_ID = 7311609911

# 15 интересных вопросов с паузой 15 секунд на ответ и 8 секунд между раундами
QUESTIONS = [
    {"text": "1. Сколько литров слюны вырабатывает организм человека за всю среднюю жизнь?", "answer": 25000},
    {"text": "2. В каком году произошла так называемая «Война из-за свиньи» между США и Великобританией?", "answer": 1859},
    {"text": "3. Сколько дней продержалась Парижская коммуна в 1871 году?", "answer": 72},
    {"text": "4. Сколько метров составляет официальная высота пирамиды Хеопса сегодня (без верхушки)?", "answer": 138},
    {"text": "5. Какое рекордное количество детей родила одна женщина в XVIII веке?", "answer": 69},
    {"text": "6. Сколько граммов весит стандартный официальный мяч для настольного тенниса?", "answer": 3},
    {"text": "7. В каком году был отправлен первый в мире SMS-текст с сообщением «Merry Christmas»?", "answer": 1992},
    {"text": "8. Сколько секунд длился самый первый успешный пилотируемый полет братьев Райт в 1903 году?", "answer": 12},
    {"text": "9. Сколько зубов у взрослой гигантской улитки (ахатины)?", "answer": 25000},
    {"text": "10. Какова средняя глубина всего мирового океана в метрах?", "answer": 3688},
    {"text": "11. В каком году состоялся первый в истории звонок по мобильному телефону?", "answer": 1973},
    {"text": "12. Сколько дней может прожить таракан без головы, пока не погибнет от жажды?", "answer": 9},
    {"text": "13. Какова максимальная зарегистрированная скорость полета сапсана при пикировании (в км/ч)?", "answer": 389},
    {"text": "14. Сколько килограммов весит сердце взрослого синего кита?", "answer": 180},
    {"text": "15. В каком году был изобретен кубик Рубика?", "answer": 1974}
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

game_running = False
round_active = False
current_answers = {}
scores = {}

@dp.message(Command("stop_game"))
async def stop_game_cmd(message: types.Message):
    global game_running, round_active
    if message.from_user.id != ADMIN_ID:
        return
    if not game_running:
        await message.answer("Игра сейчас не запущена.")
        return
    game_running = False
    round_active = False
    await message.answer("🛑 Игра принудительно остановлена ведущим!")

@dp.message(Command("start_game"))
async def start_game_cmd(message: types.Message):
    global game_running, round_active, current_answers, scores
    if message.from_user.id != ADMIN_ID:
        return
    if game_running:
        await message.answer("Игра уже идет! Чтобы остановить, напиши /stop_game")
        return

    game_running = True
    scores = {}
    await message.answer("🔥 Игра начинается! 15 редких вопросов. На каждый вопрос ровно 15 секунд!")
    await asyncio.sleep(2)

    for i, q in enumerate(QUESTIONS):
        if not game_running:
            break

        round_active = True
        current_answers = {}
        await message.answer(f"❓ Раунд {i+1}/15:\n\n{q['text']}\n\n⏱ У вас 15 секунд!")

        for _ in range(10):
            if not game_running:
                break
            await asyncio.sleep(1)

        if not game_running:
            break

        await message.answer("⚠️ Осталось 5 секунд!")

        for _ in range(5):
            if not game_running:
                break
            await asyncio.sleep(1)

        if not game_running:
            break

        round_active = False
        target = q["answer"]

        if not current_answers:
            await message.answer(f"⏰ Время вышло! Никто не дал ответ.\nТочный ответ: {target}")
            for _ in range(8):
                if not game_running:
                    break
                await asyncio.sleep(1)
            continue

        sorted_players = sorted(current_answers.items(), key=lambda item: abs(item[1] - target))
        win_text = f"⏰ Время вышло! Точный ответ: {target}\n\n🏆 Топ раунда:\n"
        points_map = [3, 2, 1]

        for idx, (user, val) in enumerate(sorted_players[:3]):
            pts = points_map[idx]
            scores[user] = scores.get(user, 0) + pts
            diff = abs(val - target)
            win_text += f"{idx+1}. {user}: {val} (разница {diff}) ➔ +{pts} очк.\n"

        await message.answer(win_text)

        for _ in range(8):
            if not game_running:
                break
            await asyncio.sleep(1)

    if game_running:
        final_text = "🏁 ИТОГОВЫЙ СЧЕТ ВСЕЙ ИГРЫ:\n\n"
        sorted_total = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (user, pts) in enumerate(sorted_total, 1):
            final_text += f"{rank}. {user} — {pts} очков\n"
        await message.answer(final_text)
        game_running = False

@dp.message()
async def collect_number(message: types.Message):
    global round_active, current_answers
    if not round_active:
        return
    text = message.text.strip().replace(" ", "")
    if text.isdigit():
        val = int(text)
        name = message.from_user.first_name or message.from_user.username
        current_answers[name] = val

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())