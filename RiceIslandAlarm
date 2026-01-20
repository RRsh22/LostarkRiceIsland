import requests
import os
from datetime import datetime

# API 키와 웹훅 URL (GitHub Secrets에서 가져옴)
API_KEY = os.environ.get('LOSTARK_API_KEY')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

# 골드를 주는 모험 섬 목록
GOLD_ISLANDS = [
    '기약의 섬',
    '고요의 섬',
    '볼라르 섬',
    '잠자는 노래의 섬',
    '죽음의 협곡'
]

def check_islands():
    # 로스트아크 API 호출
    url = "https://developer-lostark.game.onstove.com/gamecontents/calendar"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        today_gold_islands = []
        
        # 오늘 날짜의 모험 섬 중 골드 주는 섬 찾기
        for item in data:
            if item['CategoryName'] == '모험 섬':
                for reward in item.get('RewardItems', []):
                    # 골드 보상이 있는지 확인
                    if '골드' in reward.get('Name', ''):
                        island_name = item['ContentsName']
                        start_time = item['StartTimes'][0] if item.get('StartTimes') else '시간 미정'
                        today_gold_islands.append({
                            'name': island_name,
                            'time': start_time
                        })
                        break
        
        # 디스코드 알림 보내기
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
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)

if __name__ == "__main__":
    check_islands()
