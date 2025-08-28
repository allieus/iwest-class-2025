import pandas as pd

excel_path = "./assets/250825 도서목록.xlsx"

# DataFrame 타입
#  - 엑셀 중에 첫번째 시트에 대해서만 반환
df = pd.read_excel(excel_path)  # , sheet_name="")
print(df.shape)  # 행,열 수를 출력
print(df.head())  # 첫 5개행만 출력
