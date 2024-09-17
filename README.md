# LunarGanZhiCalculator
사용자의 생년월일과 시간을 입력받아 천간지지(간지)를 계산해주는 Flask 웹 애플리케이션입니다. 양력 날짜를 음력 날짜로 변환하고, 연, 월, 일, 시에 해당하는 간지를 제공합니다.

## 🚀 주요 기능

- **사용하기 쉬운 인터페이스**: 직관적인 웹 인터페이스를 통해 생년월일과 시간을 입력받습니다.
- **음력 날짜 변환**: 양력(그레고리력) 날짜를 음력 날짜로 변환합니다.
- **간지 계산**: 연, 월, 일, 시에 대한 천간지지(간지)를 계산합니다.
- **명확한 결과 표시**: 결과를 읽기 쉽고 정돈된 형식으로 제공합니다.

## 📥 설치 방법

### 필요 조건

- Python 3.x
- `pip` 패키지 관리자

### 설치 단계

1. **레포지토리 클론**

   ```bash
   git clone https://github.com/yourusername/LunarGanZhiCalculator.git
   cd LunarGanZhiCalculator
가상환경 생성 및 활성화

bash
코드 복사
python -m venv venv
source venv/bin/activate   # Windows의 경우 `venv\Scripts\activate`
필요한 패키지 설치

bash
코드 복사
pip install -r requirements.txt
requirements.txt 파일에 다음 내용이 포함되어 있는지 확인하세요:

코드 복사
Flask
lunardate
📖 사용 방법
Flask 애플리케이션 실행

bash
코드 복사
python app.py
애플리케이션 접속

웹 브라우저에서 http://localhost:5000으로 이동합니다.

생년월일과 시간 입력

출생 연도, 월, 일, 시간대를 선택합니다.
"제출" 버튼을 클릭합니다.
결과 확인

음력 생일과 연, 월, 일, 시에 해당하는 **천간지지(간지)**가 표시됩니다.
⚠️ 제한 사항
정확성: 이 애플리케이션은 간단한 계산을 제공하며, 정확한 간지 계산에 필요한 모든 복잡성을 반영하지 않을 수 있습니다.
라이브러리 의존성: 음력 날짜 변환의 정확도는 사용된 lunardate 라이브러리에 따라 달라집니다.
📄 라이선스
이 프로젝트는 MIT 라이선스에 따라 배포됩니다. 자세한 내용은 LICENSE 파일을 참고하세요.

yaml
코드 복사

---

## 🔍 **추가 안내**

- **GitHub 사용자 이름 변경**: 위의 `git clone` 명령어에서 `yourusername`을 실제 GitHub 사용자 이름으로 변경하세요.
- **LICENSE 파일 추가**: MIT 라이선스로 배포하려면 프로젝트 루트 디렉토리에 `LICENSE` 파일을 생성하고 [MIT 라이선스 내용](https://opensource.org/licenses/MIT)을 추가하세요.
- **requirements.txt 내용**: `requirements.txt` 파일에 필요한 패키지를 명시해야 합니다.

---

프로젝트 업로드와 README 작성에 도움이 되었기를 바랍니다. 프로젝트의 성공적인 진행을 기원합니다!
