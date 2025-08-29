import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel
from utils import hwp_to_html, make_response


class Person(BaseModel):
    직위: str
    성명: str
    담당업무: list[str]


class ResponseModel(BaseModel):
    persons: list[Person]


load_dotenv()

hwp_file = st.file_uploader("업무분장 HWP 파일을 업로드해주세요.")
if hwp_file is not None:
    with st.spinner("HWP 파일을 HTML로 변환 중 ..."):
        html_str = hwp_to_html(hwp_file=hwp_file)

    st.markdown(html_str, unsafe_allow_html=True)

    with st.spinner("OpenAI API를 통해 추출 중 ..."):
        user_content = "아래 HTML에서 지정 포맷을 추출해주세요.\n\n----\n\n" + html_str
        response = make_response(
            user_content=user_content,
            response_format=ResponseModel,
        )
        st.write(f"usage : {response.usage}")
        st.write(str(response.parsed))
