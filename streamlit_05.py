from dotenv import load_dotenv
import streamlit as st
from utils import make_response

load_dotenv()

user_content = st.text_input("지시사항 :") or "이미지를 설명해주세요."

image_file = st.file_uploader(
    "설명이 필요한 이미지를 업로드해주세요",
    type=["jpg", "png"],
    accept_multiple_files=False,
)

if image_file is not None:
    st.write(f"업로드 완료 : {image_file}")
    ai_content = make_response(
        user_content=user_content,
        image_file=image_file,
    )
    st.write(ai_content)
