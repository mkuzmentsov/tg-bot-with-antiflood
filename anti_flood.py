import time as tm

spams = {}
msgs = 4
max = 5
ban = 300


def is_flood(user_id):
    try:
        usr = spams[user_id]
        usr["messages"] += 1
    except:
        spams[user_id] = {"next_time": int(tm.time()) + max, "messages": 1, "banned": 0}
        usr = spams[user_id]
    if usr["banned"] >= int(tm.time()):
        return True
    else:
        if usr["next_time"] >= int(tm.time()):
            if usr["messages"] >= msgs:
                spams[user_id]["banned"] = tm.time() + ban
                return True
        else:
            spams[user_id]["messages"] = 1
            spams[user_id]["next_time"] = int(tm.time()) + max
    return False