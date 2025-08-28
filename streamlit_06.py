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
    # st.write(f"업로드 완료 : {image_file}")

    # AI 응답 대기 중 spinner 표시
    with st.spinner("AI가 응답을 생성하고 있습니다..."):
        response = make_response(
            user_content=user_content,
            image_file=image_file,
        )

    # AI 응답 표시
    st.markdown("### 🤖 AI 응답")
    st.markdown(response)

    # Usage 정보 표시 (있는 경우)
    if response.usage:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="📥 입력 토큰", value=f"{response.usage.input_tokens:,}")

        with col2:
            st.metric(label="📤 출력 토큰", value=f"{response.usage.output_tokens:,}")

        with col3:
            st.metric(label="💰 전체 토큰", value=f"{response.usage.total_tokens:,}")
