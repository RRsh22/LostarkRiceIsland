import requests
import os
from datetime import datetime, timedelta, timezone

# =====================
# 환경 변수 (GitHub Secrets)
# =====================
API_KEY = os.environ.get("LOSTARK_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# =====================
# 시간대 설정 (한국)
# =====================
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
today = now_kst.date()

# =====================
# 디스코드 전송
# =====================
def send_discord_message(embed):
    payload = {
        "embeds": [embed],
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }
    requests.post(WEBHOOK_URL, json=payload)

# =====================
# 메인 로직
# =====================
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

        gold_islands = []

        # API 응답은 리스트
        for item in data:
            if item.get("CategoryName") != "모험 섬":
                continue

            # 오늘 날짜에 해당하는 시간만 필터
            start_times = item.get("StartTimes", [])
            today_times = []

            for t in start_times:
                dt = datetime.fromisoformat(t)
                if dt.date() == today:
                    today_times.append(dt.strftime("%H:%M"))

            if not today_times:
                continue

            # 골드 보상 여부 확인
            rewards = item.get("RewardItems", [])
            has_gold = any(r.get("Name") == "골드" for r in rewards)

            if has_gold:
                gold_islands.append({
                    "name": item.get("ContentsName"),
                    "times": today_times
                })

        # =====================
        # 임베드 내용 구성
        # =====================
        description = f"📅 {today}\n\n"

        if gold_islands:
            description += "💰 **쌀섬 등장!**\n\n"

            for island in gold_islands:
                times = " / ".join(island["times"])
                description += (
                    f"📍 **{island['name']}**\n"
                    f"⏰ {times}\n\n"
                )

            description += "@everyone 쌀캐라 쌀숭이들아"
        else:
            description += "❌ 오늘은 골드 모험 섬이 없습니다."

        embed = {
            "title": "🏝️ 오늘의 모험 섬 안내",
            "description": description,
            "color": 0xF1C40F,
            "timestamp": now_kst.isoformat()
        }

        send_discord_message(embed)
        print("알림 전송 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")

# =====================
# 실행
# =====================
if __name__ == "__main__":
    check_islands()
