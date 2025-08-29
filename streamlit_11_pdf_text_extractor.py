import streamlit as st
import tempfile
import os

# PDF 라이브러리 임포트 (설치되지 않은 경우 None)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pymupdf  # PyMuPDF
except ImportError:
    pymupdf = None


# 페이지 설정
st.set_page_config(
    page_title="PDF 텍스트 추출기",
    page_icon="📄",
    layout="wide"
)

st.title("📄 PDF 텍스트 추출기")
st.markdown("다양한 Python 라이브러리를 사용하여 PDF에서 텍스트를 추출합니다.")

# 사이드바에 라이브러리 비교 정보
with st.sidebar:
    st.header("📚 라이브러리 비교")
    st.markdown("""
    ### PyPDF2
    - ✅ 가볍고 빠른 처리
    - ✅ 순수 Python 구현
    - ❌ 복잡한 레이아웃 처리 약함
    
    ### pdfplumber
    - ✅ 테이블 추출 우수
    - ✅ 레이아웃 분석 강점
    - ❌ 처리 속도 느림
    
    ### PyMuPDF
    - ✅ 가장 빠른 속도 (6배 빠름)
    - ✅ 정확한 텍스트 추출
    - ✅ 서식 보존 우수
    - ❌ AGPL 라이선스
    
    ---
    ### 권장 사용 사례
    - **간단한 텍스트**: PyPDF2
    - **테이블/레이아웃**: pdfplumber
    - **속도/정확도**: PyMuPDF
    """)


# 텍스트 추출 함수들
def extract_with_pypdf2(pdf_path):
    """PyPDF2를 사용한 텍스트 추출"""
    pages_text = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            # 진행 상황 표시
            progress_bar = st.progress(0)
            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                pages_text.append(text)
                progress_bar.progress((page_num + 1) / total_pages)
            progress_bar.empty()
            
    except Exception as e:
        raise Exception(f"PyPDF2 처리 오류: {e}")
    
    return pages_text


def extract_with_pdfplumber(pdf_path):
    """pdfplumber를 사용한 텍스트 추출"""
    pages_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            # 진행 상황 표시
            progress_bar = st.progress(0)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                pages_text.append(text or "")
                progress_bar.progress((i + 1) / total_pages)
            progress_bar.empty()
            
    except Exception as e:
        raise Exception(f"pdfplumber 처리 오류: {e}")
    
    return pages_text


def extract_with_pymupdf(pdf_path):
    """PyMuPDF를 사용한 텍스트 추출"""
    pages_text = []
    try:
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            pages_text.append(text)
            progress_bar.progress((page_num + 1) / total_pages)
        progress_bar.empty()
        
        doc.close()
    except Exception as e:
        raise Exception(f"PyMuPDF 처리 오류: {e}")
    
    return pages_text


# 메인 UI
st.header("⚙️ 설정")

# 사용 가능한 라이브러리 체크
available_libs = []
lib_status = {}

if PyPDF2:
    available_libs.append("PyPDF2")
    lib_status["PyPDF2"] = "✅ 설치됨"
else:
    lib_status["PyPDF2"] = "❌ 미설치 (pip install PyPDF2)"

if pdfplumber:
    available_libs.append("pdfplumber")
    lib_status["pdfplumber"] = "✅ 설치됨"
else:
    lib_status["pdfplumber"] = "❌ 미설치 (pip install pdfplumber)"

if pymupdf:
    available_libs.append("PyMuPDF")
    lib_status["PyMuPDF"] = "✅ 설치됨"
else:
    lib_status["PyMuPDF"] = "❌ 미설치 (pip install pymupdf)"

# 라이브러리 설치 상태 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("PyPDF2", lib_status["PyPDF2"])
with col2:
    st.metric("pdfplumber", lib_status["pdfplumber"])
with col3:
    st.metric("PyMuPDF", lib_status["PyMuPDF"])

# 사용 가능한 라이브러리가 없는 경우
if not available_libs:
    st.error("""
    ⚠️ PDF 처리 라이브러리가 설치되어 있지 않습니다.
    
    다음 명령어로 하나 이상의 라이브러리를 설치해주세요:
    ```bash
    pip install PyPDF2 pdfplumber pymupdf
    ```
    """)
    st.stop()

# 라이브러리 선택
selected_lib = st.radio(
    "PDF 처리 라이브러리 선택",
    available_libs,
    help="""각 라이브러리의 특징:
    - PyPDF2: 가볍고 빠른 기본 텍스트 추출
    - pdfplumber: 테이블과 레이아웃 분석에 강함
    - PyMuPDF: 가장 빠르고 정확한 텍스트 추출"""
)

st.markdown("---")

# PDF 파일 업로드
st.header("📤 파일 업로드")
pdf_file = st.file_uploader(
    "PDF 파일을 선택하세요",
    type=['pdf'],
    help="텍스트를 추출할 PDF 파일을 업로드하세요"
)

if pdf_file is not None:
    # 파일 정보 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📁 파일명: {pdf_file.name}")
    with col2:
        st.info(f"📊 크기: {pdf_file.size:,} bytes")
    with col3:
        st.info(f"🔧 라이브러리: {selected_lib}")
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_path = tmp_file.name
    
    # 텍스트 추출
    with st.spinner(f"{selected_lib}로 텍스트 추출 중..."):
        try:
            import time
            start_time = time.time()
            
            # 선택된 라이브러리로 추출
            if selected_lib == "PyPDF2":
                pages_text = extract_with_pypdf2(tmp_path)
            elif selected_lib == "pdfplumber":
                pages_text = extract_with_pdfplumber(tmp_path)
            else:  # PyMuPDF
                pages_text = extract_with_pymupdf(tmp_path)
            
            # 처리 시간 계산
            elapsed_time = time.time() - start_time
            
            # 통계 표시
            total_chars = sum(len(text) for text in pages_text)
            non_empty_pages = sum(1 for text in pages_text if text.strip())
            
            st.success(f"✅ 텍스트 추출 완료! (처리 시간: {elapsed_time:.2f}초)")
            
            # 추출 통계
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("총 페이지", f"{len(pages_text)}개")
            with col2:
                st.metric("텍스트 있는 페이지", f"{non_empty_pages}개")
            with col3:
                st.metric("총 문자 수", f"{total_chars:,}자")
            with col4:
                st.metric("처리 시간", f"{elapsed_time:.2f}초")
            
            st.markdown("---")
            
            # 페이지별 텍스트 표시
            st.header("📄 추출된 텍스트")
            
            # 전체 텍스트 다운로드 버튼
            all_text = "\n\n" + "="*50 + "\n\n".join([
                f"[페이지 {i}]\n{text}" 
                for i, text in enumerate(pages_text, 1)
            ])
            
            st.download_button(
                label="📥 전체 텍스트 다운로드 (TXT)",
                data=all_text,
                file_name=f"{pdf_file.name.replace('.pdf', '')}_extracted.txt",
                mime="text/plain"
            )
            
            # 페이지별 표시 옵션
            display_option = st.radio(
                "표시 옵션",
                ["모든 페이지", "텍스트가 있는 페이지만"],
                horizontal=True
            )
            
            # 페이지별 표시
            for i, text in enumerate(pages_text, 1):
                # 표시 옵션에 따라 필터링
                if display_option == "텍스트가 있는 페이지만" and not text.strip():
                    continue
                
                # 페이지 헤더와 문자 수 표시
                page_char_count = len(text)
                page_word_count = len(text.split()) if text.strip() else 0
                
                with st.expander(
                    f"📄 페이지 {i} "
                    f"({page_char_count:,}자, {page_word_count:,}단어)"
                ):
                    if text.strip():
                        # 텍스트를 컨테이너에 표시
                        text_container = st.container()
                        with text_container:
                            # 텍스트 미리보기 (처음 500자)
                            if len(text) > 500:
                                preview_text = text[:500] + "..."
                                full_view = st.checkbox(
                                    "전체 텍스트 보기", 
                                    key=f"full_view_{i}"
                                )
                                if full_view:
                                    st.text_area(
                                        "추출된 텍스트",
                                        text,
                                        height=400,
                                        key=f"text_{i}"
                                    )
                                else:
                                    st.text_area(
                                        "추출된 텍스트 (미리보기)",
                                        preview_text,
                                        height=200,
                                        key=f"preview_{i}"
                                    )
                            else:
                                st.text_area(
                                    "추출된 텍스트",
                                    text,
                                    height=200,
                                    key=f"text_{i}"
                                )
                            
                            # 페이지별 다운로드 버튼
                            st.download_button(
                                label=f"📥 페이지 {i} 다운로드",
                                data=text,
                                file_name=f"{pdf_file.name.replace('.pdf', '')}_page_{i}.txt",
                                mime="text/plain",
                                key=f"download_{i}"
                            )
                    else:
                        st.info("💭 이 페이지에는 추출 가능한 텍스트가 없습니다.")
                        
        except Exception as e:
            st.error(f"❌ 텍스트 추출 실패: {e}")
            
        finally:
            # 임시 파일 삭제
            try:
                os.unlink(tmp_path)
            except:
                pass

else:
    # 업로드 전 안내 메시지
    st.info("""
    👆 PDF 파일을 업로드하면 텍스트 추출이 시작됩니다.
    
    **지원 기능:**
    - 페이지별 텍스트 추출
    - 접기/펼치기 가능한 페이지 뷰
    - 텍스트 다운로드 (전체/페이지별)
    - 추출 통계 표시
    """)
    
    # 샘플 파일 안내
    if os.path.exists("PDFs"):
        pdf_files = [f for f in os.listdir("PDFs") if f.endswith('.pdf')]
        if pdf_files:
            st.markdown("---")
            st.markdown("### 📁 샘플 파일")
            st.markdown("PDFs 폴더에서 다음 파일들을 테스트할 수 있습니다:")
            for pdf in pdf_files[:5]:  # 최대 5개만 표시
                st.code(f"PDFs/{pdf}")