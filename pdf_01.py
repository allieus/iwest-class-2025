import PyPDF2


# 들여쓰기 (Indentation)
def get_pdf_info(pdf_path: str) -> dict:
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)

        title = reader.metadata.get("/Title", "")
        author = reader.metadata.get("/Author", "")
        subject = reader.metadata.get("/Subject", "")

        page_content_list = []
        for page_no, page in enumerate(reader.pages, start=1):
            page_content: str = page.extract_text()
            page_content_list.append(page_content)
            # print(f"## 페이지 {page_no} ##")
            # print(page_content)
            # print()

        return {
            "title": title,
            "author": author,
            "subject": subject,
            "page_content_list": page_content_list,
        }


def main():
    pdf_path = "./PDFs/1GJCC9-36110-BC-301-515_Foundation Load Calculation for Surface Condenser_Rev.A.pdf"
    info = get_pdf_info(pdf_path)
    print(info["title"])


main()
