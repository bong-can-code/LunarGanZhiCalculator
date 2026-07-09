from flask import Flask, jsonify, render_template, request

from saju import calculate_saju

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
    except (KeyError, ValueError):
        return jsonify({'error': '생년월일을 올바르게 입력해 주세요.'}), 400

    is_lunar = request.form.get('calendarType') == 'lunar'
    is_leap_month = request.form.get('leapMonth') == 'true'

    # 시간: "13-15" 범위의 시작 시각 사용. "unknown"이면 시주 생략.
    hour_range = request.form.get('hour', 'unknown')
    if hour_range == 'unknown':
        hour = None
    else:
        try:
            hour = int(hour_range.split('-')[0])
        except ValueError:
            hour = None

    try:
        result = calculate_saju(
            year, month, day, hour,
            is_lunar=is_lunar, is_leap_month=is_leap_month,
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
