import requests
import os
import sys
from datetime import datetime, timedelta, timezone

# =====================
# GitHub Actions 트리거 가드
# =====================
EVENT_NAME = os.environ.get("GITHUB_EVENT_NAME")
if EVENT_NAME != "schedule":
    print(f"[INFO] Triggered by {EVENT_NAME}, skip sending message.")
    sys.exit(0)

# =====================
# 환경 변수
# =====================
API_KEY = os.environ.get("LOSTARK_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not API_KEY or not WEBHOOK_URL:
    print("❌ 환경 변수 누락")
    sys.exit(1)

# =====================
# 시간 설정 (KST 기준 날짜 계산용)
# =====================
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
today = now_kst.date()
weekday = now_kst.weekday()  # 월=0, 토=5, 일=6

# =====================
# 모험 섬 시간 그룹 정의
# =====================
WEEKDAY_TIMES = {"11:00", "13:00", "19:00", "21:00", "23:00"}
WEEKEND_GROUP_A = {"09:00", "11:00", "13:00"}
WEEKEND_GROUP_B = {"19:00", "21:00", "23:00"}

# =====================
# 디스코드 전송
# =====================
def send_discord_message(embed):
    requests.post(
        WEBHOOK_URL,
        json={
            "embeds": [embed],
            "allowed_mentions": {"parse": ["everyone"]}
        }
    )

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

        # 오늘 열리는 시간 수집
        today_times = set()
        for t in item.get("StartTimes", []):
            dt = datetime.fromisoformat(t)
            if dt.date() == today:
                today_times.add(dt.strftime("%H:%M"))

        if not today_times:
            continue

        # 시간 그룹 판별
        if weekday < 5:
            final_times = today_times & WEEKDAY_TIMES
        else:
            group_a = today_times & WEEKEND_GROUP_A
            group_b = today_times & WEEKEND_GROUP_B

            if group_a:
                final_times = group_a
            elif group_b:
                final_times = group_b
            else:
                continue

        if not final_times:
            continue

        # 골드 보상이 실제로 해당 시간대에 있는지 확인
        has_gold = False

        for reward_group in item.get("RewardItems", []):
            for reward in reward_group.get("Items", []):
                if reward.get("Name") != "골드":
                    continue

                for rt in reward.get("StartTimes", []) or []:
                    rt_dt = datetime.fromisoformat(rt)
                    if rt_dt.date() == today:
                        if rt_dt.strftime("%H:%M") in final_times:
                            has_gold = True
                            break

                if has_gold:
                    break
            if has_gold:
                break

        if has_gold:
            gold_islands.append({
                "name": item.get("ContentsName"),
                "times": sorted(final_times)
            })

    # =====================
    # 디스코드 메시지 구성
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
