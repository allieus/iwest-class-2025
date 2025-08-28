from dotenv import load_dotenv
import streamlit as st
from utils import make_response

load_dotenv()

st.title("한국서부발전")

st.markdown(
    """
안녕하세요. 저는 이진석 대리입니다.
좋아하는 과일은

+ 사과
+ 바나나
+ 딸기            
"""
)

question = st.text_input("질문을 입력하세요.")

if st.button("전송") and question:
    # OpenAI API 활용 : 폐쇄망에서는 사용 불가.
    # 폐쇄망이라면 : 다운로드 오픈소스 모델을 활용 (ollama)
    ai_content = make_response(user_content=question)
    st.write(f"AI : {ai_content}")
