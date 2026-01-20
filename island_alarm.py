import requests
import os
from datetime import datetime

API_KEY = os.environ.get('LOSTARK_API_KEY')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def check_islands():
    url = "https://developer-lostark.game.onstove.com/gamecontents/calendar"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }

    today = datetime.now().date()

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    today_gold_islands = []

    for item in data:
        if item.get("CategoryName") != "모험 섬":
            continue

        island_name = item.get("ContentsName")

        # 오늘 시간만 필터
        today_times = []
        for t in item.get("StartTimes", []):
            t_date = datetime.fromisoformat(t).date()
            if t_date == today:
                today_times.append(t[11:16])  # HH:MM만

        if not today_times:
            continue

        # 골드 여부 확인
        has_gold = False
        for reward_group in item.get("RewardItems", []):
            for reward in reward_group.get("Items", []):
                if reward.get("Name") == "골드":
                    has_gold = True
                    break

        if has_gold:
            today_gold_islands.append({
                "name": island_name,
                "times": today_times
            })

    if not today_gold_islands:
        print("오늘은 골드 모험 섬이 없습니다.")
        return

    message = "🏝️ **오늘의 골드 모험 섬** 🏝️\n\n"
    for island in today_gold_islands:
        message += f"📍 **{island['name']}**\n"
        message += f"⏰ {' / '.join(island['times'])}\n\n"

    send_discord_message(message)
    print("알림 전송 완료!")

def send_discord_message(message):
    requests.post(WEBHOOK_URL, json={"content": message})

if __name__ == "__main__":
    check_islands()
