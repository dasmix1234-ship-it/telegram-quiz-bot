import telebot
import threading
import time
import os
from flask import Flask

# Вставь сюда токен твоего бота
TOKEN = '8223693755:AAH-cCy7_kzwtf_E1oMiyBsH7pfZi7yU_UU'
bot = telebot.TeleBot(TOKEN)

# Настройка Flask для поддержания бота в сети
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Бот работает!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Состояние игры
game_state = {
    "is_active": False,
    "chat_id": None,
    "current_q_index": 0,
    "answers": {}, 
    "scores": {}   
}

# 20 вопросов на интуицию
questions = [
    {"text": "Сколько весит среднее кучевое облако (в тоннах)?", "answer": 500},
    {"text": "Сколько секунд длился самый первый полет братьев Райт?", "answer": 12},
    {"text": "Сколько раз в секунду машет крыльями колибри в полете?", "answer": 80},
    {"text": "Какое количество слов использует в повседневной речи среднестатистический человек в день?", "answer": 16000},
    {"text": "Сколько зубов у обычной садовой улитки?", "answer": 14000},
    {"text": "Сколько километров в день пролетает медоносная пчела за нектаром?", "answer": 8},
    {"text": "Сколько длился самый длинный официально зарегистрированный полет курицы (в секундах)?", "answer": 13},
    {"text": "Сколько мышц используется, чтобы улыбнуться?", "answer": 17},
    {"text": "На какую глубину в метрах может нырнуть императорский пингвин?", "answer": 500},
    {"text": "Сколько дней может проспать улитка без еды, находясь в спячке?", "answer": 1095},
    {"text": "Какая температура (в градусах Цельсия) на поверхности Солнца?", "answer": 5500},
    {"text": "Сколько ударов в минуту делает сердце синего кита?", "answer": 9},
    {"text": "Сколько зубов у комара?", "answer": 47},
    {"text": "Сколько раз бьет молния на Земле каждую секунду?", "answer": 100},
    {"text": "Сколько литров слюны вырабатывает человек за всю жизнь (в тысячах)?", "answer": 23},
    {"text": "Какова длина всех кровеносных сосудов человека (в тысячах километров)?", "answer": 100},
    {"text": "Сколько костей в теле взрослой акулы?", "answer": 0},
    {"text": "Какой процент объема арбуза составляет вода?", "answer": 92},
    {"text": "Сколько лет было самому старому человеку в мире, чей возраст официально подтвержден?", "answer": 122},
    {"text": "Сколько часов в сутки в среднем спит коала?", "answer": 20}
]

@bot.message_handler(commands=['start_game'])
def start_game(message):
    if game_state["is_active"]:
        bot.send_message(message.chat.id, "Игра уже идет! Дождитесь окончания.")
        return
        
    game_state["is_active"] = True
    game_state["chat_id"] = message.chat.id
    game_state["current_q_index"] = 0
    game_state["scores"] = {}
    
    bot.send_message(
        message.chat.id, 
        "🚀 Игра началась! \n"
        "Пишите числа. Кто ближе к ответу и быстрее — забирает баллы!\n"
        "🥇 1 место — 3 балла\n🥈 2 место — 2 балла\n🥉 3 место — 1 балл"
    )
    time.sleep(2)
    ask_question()

@bot.message_handler(commands=['stop_game'])
def stop_game(message):
    if not game_state["is_active"]:
        bot.send_message(message.chat.id, "Игра сейчас не запущена.")
        return
    end_game()

def ask_question():
    if not game_state["is_active"]:
        return
        
    index = game_state["current_q_index"]
    if index >= len(questions):
        end_game()
        return
        
    q = questions[index]
    game_state["answers"].clear()
    
    bot.send_message(
        game_state["chat_id"], 
        f"❓ Вопрос {index + 1}/20:\n\n{q['text']}\n\n⏳ У вас 15 секунд!"
    )
    
    # Запускаем таймер на 15 секунд
    threading.Timer(15.0, finish_round).start()

def finish_round():
    if not game_state["is_active"]:
        return
        
    q = questions[game_state["current_q_index"]]
    target = q["answer"]
    
    if not game_state["answers"]:
        bot.send_message(game_state["chat_id"], f"Никто не дал ответа! 😢\nПравильный ответ: {target}")
    else:
        # Собираем ответы в список: (user_id, разница, время_ответа, имя, ответ_пользователя)
        results = []
        for uid, data in game_state["answers"].items():
            diff = abs(data["answer"] - target)
            results.append((uid, diff, data["timestamp"], data["name"], data["answer"]))
            
        # Сортируем: сначала по минимальной разнице, затем по времени ответа (кто быстрее)
        results.sort(key=lambda x: (x[1], x[2]))
        
        # Берем только топ-3
        top_3 = results[:3]
        points_dist = [3, 2, 1]
        
        msg = f"✅ Правильный ответ: {target}\n\n🏆 Топ раунда:\n"
        
        # Начисляем баллы и формируем сообщение
        for i, res in enumerate(top_3):
            uid, diff, ts, name, ans = res
            points = points_dist[i]
            
            if uid not in game_state["scores"]:
                game_state["scores"][uid] = {"name": name, "score": 0}
            game_state["scores"][uid]["score"] += points
            
            medals = ["🥇", "🥈", "🥉"]
            msg += f"{medals[i]} {name} (ответ: {ans}) — +{points} балл(а)\n"
            
        bot.send_message(game_state["chat_id"], msg)
        
    game_state["current_q_index"] += 1
    
    if game_state["current_q_index"] < len(questions):
        bot.send_message(game_state["chat_id"], "Следующий вопрос через 8 секунд... Готовьтесь!")
        time.sleep(8) # Пауза ровно 8 секунд
        ask_question()
    else:
        end_game()

def end_game():
    game_state["is_active"] = False
    
    if not game_state["scores"]:
        bot.send_message(game_state["chat_id"], "🏁 Игра окончена! Никто не заработал баллов.")
        return
        
    # Сортируем победителей по общему количеству баллов
    sorted_players = sorted(game_state["scores"].values(), key=lambda x: x["score"], reverse=True)
    
    results = "🏁 Игра окончена! Итоговый счет:\n\n"
    for idx, p in enumerate(sorted_players, 1):
        results += f"{idx}. {p['name']} — {p['score']} очков\n"
        
    bot.send_message(game_state["chat_id"], results)

@bot.message_handler(func=lambda m: game_state["is_active"] and m.chat.id == game_state["chat_id"])
def handle_text(message):
    try:
        text_num = message.text.strip().replace(',', '.')
        number = float(text_num)
        
        # Сохраняем ответ и точную метку времени (для определения скорости)
        game_state["answers"][message.from_user.id] = {
            "name": message.from_user.first_name,
            "answer": number,
            "timestamp": time.time()
        }
    except ValueError:
        pass 

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("Бот запущен...")
    bot.polling(none_stop=True)
