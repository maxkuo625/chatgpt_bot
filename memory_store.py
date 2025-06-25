# 簡單以記憶體字典模擬，實際可改為 Redis、MongoDB 等
user_memory = {}

def get_user_context(user_id):
    return user_memory.get(user_id, [])

def update_user_context(user_id, message):
    history = user_memory.get(user_id, [])
    history.append(message)
    if len(history) > 10:  # 限制記憶長度
        history = history[-10:]
    user_memory[user_id] = history
