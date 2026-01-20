import requests
import os

API_KEY = os.environ.get('LOSTARK_API_KEY')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def check_islands():
    url = "https://developer-lostark.game.onstove.com/gamecontents/calendar"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        today_gold_islands = []

        for item in data:
            if item.get("CategoryName") != "모험 섬":
                continue

            island_name = item.get("ContentsName")
            start_times = item.get("StartTimes", [])

            for reward_group in item.get("RewardItems", []):
                for reward in reward_group.get("Items", []):
                    if reward.get("Name") == "골드":
                        today_gold_islands.append({
                            "name": island_name,
                            "time": ", ".join(start_times),
                            "gold": reward.get("Count")
                        })
                        break

        if today_gold_islands:
            message = "🏝️ **오늘의 골드 모험 섬** 🏝️\n\n"
            for island in today_gold_islands:
                message += (
                    f"📍 **{island['name']}**\n"
                    f"⏰ {island['time']}\n"
                    f"💰 골드 {island['gold']}개\n\n"
                )

            send_discord_message(message)
            print("알림 전송 완료!")
        else:
            print("오늘은 골드 모험 섬이 없습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

def send_discord_message(message):
    requests.post(WEBHOOK_URL, json={"content": message})

if __name__ == "__main__":
    check_islands()
