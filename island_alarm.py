import requests
import os
import sys
from datetime import datetime, timedelta, timezone

# =====================
# 환경 변수
# =====================
API_KEY = os.environ.get("LOSTARK_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not API_KEY or not WEBHOOK_URL:
    print("❌ 환경 변수 누락")
    sys.exit(1)

# =====================
# 시간대 설정
# =====================
UTC = timezone.utc
KST = timezone(timedelta(hours=9))

now_kst = datetime.now(KST)
today = now_kst.date()

# =====================
# 10:30 이전 실행 차단
# =====================
TARGET_TIME = now_kst.replace(hour=10, minute=30, second=0, microsecond=0)
if now_kst < TARGET_TIME:
    print("⏳ 10:30 이전 실행 → 종료")
    sys.exit(0)

# =====================
# 디스코드 전송
# =====================
def send_discord_message(embed):
    payload = {
        "embeds": [embed],
        "allowed_mentions": {"parse": ["everyone"]}
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

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    gold_islands = []

    for item in data:
        if item.get("CategoryName") != "모험 섬":
            continue

        # 오늘(KST) 시간 필터
        today_times = []
        for t in item.get("StartTimes", []):
            dt = datetime.fromisoformat(t).replace(tzinfo=UTC).astimezone(KST)
            if dt.date() == today:
                today_times.append(dt.strftime("%H:%M"))

        if not today_times:
            continue

        # =====================
        # ✅ 올바른 골드 판별
        # =====================
        has_gold = False

        for reward_group in item.get("RewardItems", []):
            for reward in reward_group.get("Items", []):
                if reward.get("Name") == "골드":
                    has_gold = True
                    break

        if has_gold:
            gold_islands.append({
                "name": item.get("ContentsName"),
                "times": sorted(today_times)
            })

    # =====================
    # 디스코드 메시지
    # =====================
    description = f"📅 {today}\n\n"

    if gold_islands:
        description += "💰 **오늘의 골드 모험 섬**\n\n"
        for island in gold_islands:
            description += (
                f"📍 **{island['name']}**\n"
                f"⏰ {' / '.join(island['times'])}\n\n"
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
    print("✅ 알림 전송 완료")

# =====================
# 실행
# =====================
if __name__ == "__main__":
    check_islands()
