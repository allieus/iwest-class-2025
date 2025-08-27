# iwest-class-2025

## 프로젝트 개요

이 저장소는 Python을 활용한 파일 다운로드, 웹 크롤링, OpenAI API 연동 예제 및 유틸리티 함수 등을 포함한 실습용 코드 모음입니다.

## 프로젝트 구조

```
hello_01.py         # 파일 다운로드 예제 (requests 사용)
hello_02.py         # 웹페이지에서 파일 링크 추출 및 다운로드 (BeautifulSoup, utils.download_file 사용)
hello_ai_01.py      # OpenAI 챗봇 API 연동(단일 메시지)
hello_ai_02.py      # OpenAI 챗봇 API 연동(대화형, 반복 입력)
utils.py            # 파일 다운로드 함수, 곱셈 함수 등 유틸리티
requirements.txt    # 필요한 Python 패키지 목록
```

## 가상환경 생성 및 활성화 (Windows 기준)

1. 가상환경 생성

```
python -m venv venv
```

2. 가상환경 활성화

```
venv\Scripts\activate
```

3. 패키지 설치

```
pip install -r requirements.txt
```

## 실행 예시

- 파일 다운로드:
  ```
  python hello_01.py
  ```
- 웹 크롤링 및 파일 다운로드:
  ```
  python hello_02.py
  ```
- OpenAI 챗봇(단일 메시지):
  ```
  python hello_ai_01.py
  ```
- OpenAI 챗봇(대화형):
  ```
  python hello_ai_02.py
  ```

## 주요 패키지
- openai
- requests
- beautifulsoup4
- python-dotenv
- streamlit
- jupyter

## 참고
- .env 파일에 OpenAI API 키(OPENAI_API_KEY)를 저장해야 OpenAI 관련 예제가 동작합니다.

## 라이선스
- 본 저장소는 교육 및 실습 목적입니다.
