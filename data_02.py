import pandas as pd
import streamlit as st

excel_file = st.file_uploader(
    "분석할 엑셀 파일을 업로드해주세요",
    type=["xls", "xlsx"],
    accept_multiple_files=False,
)
if excel_file is not None:
    df = pd.read_excel(excel_file)  # , sheet_name="")
    # df 후가공해서 가공한 결과 DataFrame 생성 후에 보여줄 수도 있습니다.
    st.dataframe(df)
