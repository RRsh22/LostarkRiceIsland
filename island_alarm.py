import requests
import os

API_KEY = os.environ.get('LOSTARK_API_KEY')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def check_islands():
    url = "https://developer-lostark.game.onstove.com/gamecontents/calendar"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        today_gold_islands = []

        for item in data.get("Calendar", []):
            if item.get("CategoryName") == "모험 섬":
                for reward in item.get("RewardItems", []):
                    if reward.get("Name") == "골드":
                        island_name = item.get("ContentsName")
                        start_time = (
                            item.get("StartTimes")[0]
                            if item.get("StartTimes")
                            else "시간 미정"
                        )

                        today_gold_islands.append({
                            "name": island_name,
                            "time": start_time
                        })
                        break

        if today_gold_islands:
            message = "🏝️ **오늘의 골드 모험 섬** 🏝️\n\n"
            for island in today_gold_islands:
                message += f"📍 **{island['name']}** - {island['time']}\n"

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
