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
# 시간 설정 (KST 기준)
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
    try:
        requests.post(
            WEBHOOK_URL,
            json={
                "embeds": [embed],
                "allowed_mentions": {"parse": ["everyone"]}
            },
            timeout=10
        )
    except Exception as e:
        print(f"디스코드 전송 실패: {e}")

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
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"API 요청 실패: {e}")
        sys.exit(1)

    gold_islands = []

    for item in (data or []):
        if not isinstance(item, dict):
            continue

        if item.get("CategoryName") != "모험 섬":
            continue

        # =====================
        # 오늘 열리는 시간 수집 (None 방어)
        # =====================
        today_times = set()
        for t in (item.get("StartTimes") or []):
            try:
                dt = datetime.fromisoformat(t)
                if dt.date() == today:
                    today_times.add(dt.strftime("%H:%M"))
            except Exception:
                continue

        if not today_times:
            continue

        # =====================
        # 시간 그룹 판별 (주말 구조 완벽 대응)
        # =====================
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

        # =====================
        # 골드 보상 (시간대 일치하는 것만)
        # =====================
        has_gold = False

        for reward_group in (item.get("RewardItems") or []):
            if not isinstance(reward_group, dict):
                continue

            for reward in (reward_group.get("Items") or []):
                if not isinstance(reward, dict):
                    continue

                if reward.get("Name") != "골드":
                    continue

                for rt in (reward.get("StartTimes") or []):
                    try:
                        rt_dt = datetime.fromisoformat(rt)
                        if rt_dt.date() == today:
                            if rt_dt.strftime("%H:%M") in final_times:
                                has_gold = True
                                break
                    except Exception:
                        continue

                if has_gold:
                    break
            if has_gold:
                break

        if has_gold:
            gold_islands.append({
                "name": item.get("ContentsName", "알 수 없는 섬"),
                "times": sorted(final_times)
            })

    # =====================
    # 디스코드 메시지 생성
    # =====================
    description = f"📅 {today} (KST)\n\n"

    if gold_islands:
        description += "💰 **오늘의 골드 모험 섬**\n\n"
        for island in gold_islands:
            description += (
                f"📍 **{island['name']}**\n"
                f"⏰ {' / '.join(island['times'])}\n\n"
            )
        description += "@everyone 쌀 캐라 쌀숭이들아"
    else:
        description += "❌ 오늘은 골드 모험 섬이 없습니다."

    embed = {
        "title": "🏝️ 로스트아크 모험 섬 알림",
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
