from datetime import datetime, timedelta

def get_streak_list(data:list):
    if not data:
        return []
    k=1
    streaks = []
    for i in range(len(data)-1):
        if data[i] + timedelta(days=1) == data[i+1]:
            k+=1
        else:
            streaks.append(k)
            k=1
    streaks.append(k)

    return streaks

