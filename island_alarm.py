import requests
import os
from datetime import datetime, timedelta, timezone

API_KEY = os.environ.get("LOSTARK_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))

def check_islands():
    url = "https://developer-lostark.game.onstove.com/gamecontents/calendar"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }

    now_kst = datetime.now(KST)
    today = now_kst.date()

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    gold_islands = []

    for item in data:
        if item.get("CategoryName") != "모험 섬":
            continue

        island_name = item.get("ContentsName")

        # 오늘 시간만 추출
        today_times = []
        for t in item.get("StartTimes", []):
            t_dt = datetime.fromisoformat(t)
            if t_dt.date() == today:
                today_times.append(t_dt.strftime("%H:%M"))

        if not today_times:
            continue

        # 골드 보상 여부 확인
        has_gold = False
        for reward_group in item.get("RewardItems", []):
            for reward in reward_group.get("Items", []):
                if reward.get("Name") == "골드":
                    has_gold = True
                    break

        if has_gold:
            gold_islands.append({
                "name": island_name,
                "times": today_times
            })

    send_discord_message(gold_islands, now_kst)

def send_discord_message(gold_islands, now_kst):
    today_str = now_kst.strftime("%Y-%m-%d")

    # 골드섬 있는 날
    if gold_islands:
        content = "@everyone"
        embed = {
            "title": "🏝️ 오늘의 골드 모험 섬",
            "color": 0xFFD700,
            "description": f"📅 {today_str}",
            "fields": [],
            "footer": {
                "text": "로스트아크 모험 섬 알림 봇"
            }
        }

        for island in gold_islands:
            embed["fields"].append({
                "name": island["name"],
                "value": "⏰ " + " / ".join(island["times"]),
                "inline": False
            })

    # 골드섬 없는 날
    else:
        content = ""
        embed = {
            "title": "🏝️ 오늘의 모험 섬 안내",
            "color": 0x9E9E9E,
            "description": (
                f"📅 {today_str}\n\n"
                "❌ 오늘은 **골드 모험 섬이 없습니다**."
            ),
            "footer": {
                "text": "로스트아크 모험 섬 알림 봇"
            }
        }

    payload = {
        "content": content,
        "embeds": [embed]
    }

    requests.post(WEBHOOK_URL, json=payload)
    print("알림 전송 완료!")

if __name__ == "__main__":
    check_islands()
