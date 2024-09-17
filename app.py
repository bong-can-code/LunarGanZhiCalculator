from flask import Flask, render_template, request
from datetime import datetime
from lunardate import LunarDate

app = Flask(__name__)

# 천간과 지지 리스트
heavenly_stems = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
earthly_branches = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    year = int(request.form['year'])
    
    month = int(request.form['month'])
    
    day = int(request.form['day'])

    # 시간 값 처리: "13-15" 같은 범위를 받았을 때 첫 번째 시간만 사용
    hour_range = request.form['hour']
    # "13-15" 형식에서 첫 번째 시간을 추출
    hour = int(hour_range.split('-')[0])

    lunar_date = LunarDate.fromSolarDate(year, month, day)
    result = f"음력 날짜: {lunar_date.year}년 {lunar_date.month}월 {lunar_date.day}일"
    return result

if __name__ == '__main__':
    app.run(debug=True)
