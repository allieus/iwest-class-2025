import os
import mimetypes
import requests
from base64 import b64encode
from dataclasses import dataclass
from typing import BinaryIO, Protocol
from openai import OpenAI
from openai.types.shared.chat_model import ChatModel


class FileUploadProtocol(Protocol):
    """파일 업로드 객체의 프로토콜 정의.

    Streamlit의 UploadedFile, Flask의 FileStorage 등을 지원합니다.
    """

    @property
    def name(self) -> str: ...  # 파일명
    @property
    def type(self) -> str: ...  # MIME 타입
    def read(self) -> bytes: ...  # 파일 내용 읽기


@dataclass
class Usage:
    """API 사용량 정보를 담는 클래스.

    Attributes:
        input_tokens: 입력 토큰 수 (prompt_tokens)
        output_tokens: 출력 토큰 수 (completion_tokens)
        total_tokens: 전체 토큰 수
    """

    input_tokens: int
    output_tokens: int
    total_tokens: int


class ResponseWithUsage(str):
    """문자열처럼 동작하면서 usage 정보를 포함하는 응답 클래스.

    일반 문자열처럼 사용할 수 있으며, 추가로 usage 속성을 통해
    토큰 사용량 정보에 접근할 수 있습니다.
    """

    def __new__(cls, content: str, usage: Usage | None = None):
        """ResponseWithUsage 인스턴스 생성.

        Args:
            content: 응답 내용 문자열
            usage: 토큰 사용량 정보 (선택사항)

        주의: __init__ 대신 __new__를 사용하는 이유
        - str은 불변(immutable) 객체라서 생성 후에는 값을 변경할 수 없음
        - __new__는 객체 생성 시점에 호출되어 str 값을 설정 가능
        - __init__은 객체 생성 후 호출되므로 str 값 변경 불가
        """
        # 1. str 타입의 인스턴스를 content 값으로 생성
        instance = super().__new__(cls, content)
        # 2. 생성된 인스턴스에 usage 정보를 속성으로 추가
        instance._usage = usage
        # 3. 완성된 인스턴스 반환
        return instance

    @property
    def usage(self) -> Usage | None:
        """토큰 사용량 정보를 반환합니다."""
        return self._usage


def get_mime_type(file_path: str) -> str:
    """파일 경로에서 MIME 타입을 추론합니다.

    Args:
        file_path (str): 파일 경로

    Returns:
        str: MIME 타입 문자열

    Note:
        확장자 기반으로 추론하며, 알 수 없는 확장자의 경우
        'application/octet-stream'을 반환합니다.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def make_response(
    user_content: str,
    file_path: str | None = None,  # 새로운 범용 파일 경로 (이미지/PDF)
    file: (
        FileUploadProtocol | BinaryIO | None
    ) = None,  # 새로운 범용 파일 객체 (이미지/PDF)
    image_path: str | None = None,  # 호환성 유지
    image_file: FileUploadProtocol | BinaryIO | None = None,  # 호환성 유지
    system_content: str | None = None,
    model: str | ChatModel = "gpt-4o-mini",
    temperature: float = 0.25,
    api_key: str | None = None,
) -> ResponseWithUsage:
    """OpenAI의 Chat Completion API를 사용하여 AI의 응답을 생성합니다.

    이미지 파일(.png, .jpg, .jpeg)과 PDF 파일을 지원합니다.

    Args:
        user_content (str): 사용자 메시지.
        file_path (str | None, optional): 파일 경로 (이미지/PDF). 기본값은 None.
        file (FileUploadProtocol | BinaryIO | None, optional): 파일 객체 (이미지/PDF). 기본값은 None.
        image_path (str | None, optional): 이미지 파일 경로 (호환성용). 기본값은 None.
        image_file (FileUploadProtocol | BinaryIO | None, optional): 이미지 파일 객체 (호환성용). 기본값은 None.
        system_content (str | None, optional): 시스템 메시지. 기본값은 None.
        model (str | ChatModel, optional): 사용할 모델. 기본값은 "gpt-4o-mini".
        temperature (float, optional): 생성 결과의 창의성. 기본값은 0.25.
        api_key (str | None, optional): OpenAI API 키. 기본값은 None.

    Returns:
        ResponseWithUsage: AI가 생성한 응답 메시지. 문자열처럼 사용 가능하며,
            .usage 속성을 통해 토큰 사용량 정보에 접근할 수 있습니다.

    Examples:
        >>> response = make_response("안녕하세요")
        >>> print(response)  # "안녕하세요! 무엇을 도와드릴까요?"
        >>> print(response.usage.input_tokens)  # 10
        >>> print(response.usage.output_tokens)  # 15
    """
    # 1. 호환성 처리 (간단하게)
    file_path = file_path or image_path
    file = file or image_file

    # 2. 메시지 리스트 초기화
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})

    # 3. 사용자 메시지 구성
    user_message_content = user_content  # 기본값: 텍스트만

    if file_path or file:
        # 파일 정보 추출 (삼항 연산자 활용)
        filename = os.path.basename(file_path) if file_path else file.name
        mime_type = get_mime_type(file_path) if file_path else file.type

        # base64 URL 생성
        base64_url = make_base64_url(file_path=file_path, file=file)

        # 파일 딕셔너리 생성 (삼항 연산자로 단순화)
        file_dict = (
            {
                "type": "image_url",
                "image_url": {"url": base64_url, "detail": "high"},
            }
            if mime_type.startswith("image/")
            else {
                "type": "file",
                "file": {"filename": filename, "file_data": base64_url},
            }
        )

        # 텍스트와 파일을 포함한 content 구성
        user_message_content = [
            {"type": "text", "text": user_content},
            file_dict,
        ]

    messages.append({"role": "user", "content": user_message_content})

    # 4. API 호출
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    # 5. Usage 정보 추출 및 반환
    usage = (
        Usage(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
        )
        if response.usage
        else None
    )

    return ResponseWithUsage(
        content=response.choices[0].message.content or "",
        usage=usage,
    )


def download_file(
    file_url: str,
    filepath: str | None = None,  # default parameter
) -> None:
    """URL로부터 파일을 다운로드하여 로컬에 저장합니다.

    Args:
        file_url (str): 다운로드할 파일의 URL.
        filepath (str | None, optional): 저장할 파일 경로.
            None인 경우 URL의 파일명을 사용합니다. 기본값은 None.

    Returns:
        None

    Note:
        동일한 경로에 파일이 이미 존재할 경우 덮어씁니다.
    """
    res = requests.get(file_url)
    print("res ok :", res.ok)

    if filepath is None:
        filepath = os.path.basename(file_url)

    file_content = res.content

    dir_path = os.path.dirname(filepath)
    os.makedirs(dir_path, exist_ok=True)

    # 주의 : 같은 경로의 경로일 경우, 덮어쓰기가 됩니다.
    with open(filepath, "wb") as f:
        f.write(file_content)
        print("saved", filepath)


def multiply(a: int, b: int) -> int:
    """두 개의 숫자를 곱한 결과를 반환합니다.

    Args:
        a (int): 첫 번째 숫자.
        b (int): 두 번째 숫자.

    Returns:
        int: a와 b를 곱한 값.
    """
    return a * b


def make_base64_url(
    file_path: str | None = None,
    file: FileUploadProtocol | BinaryIO | None = None,
    image_path: str | None = None,  # deprecated but kept for compatibility
    image_file: (
        FileUploadProtocol | BinaryIO | None
    ) = None,  # deprecated but kept for compatibility
) -> str:
    """파일을 base64 URL로 변환합니다.

    Args:
        file_path (str | None): 파일 경로 (새로운 방식)
        file (FileUploadProtocol | BinaryIO | None): 파일 객체 (새로운 방식)
        image_path (str | None): 이미지 파일 경로 (호환성 유지)
        image_file (FileUploadProtocol | BinaryIO | None): 이미지 파일 객체 (호환성 유지)

    Returns:
        str: base64로 인코딩된 data URL
    """
    # 호환성: 기존 인자가 있으면 새 인자로 매핑
    if image_path and not file_path:
        file_path = image_path
    if image_file and not file:
        file = image_file

    if file_path:
        # 파일 경로에서 MIME 타입 추론
        mime_type = get_mime_type(file_path)
        with open(file_path, "rb") as f:
            data: bytes = f.read()
    elif file:
        # 파일 객체에서 MIME 타입 가져오기
        mime_type = file.type if hasattr(file, "type") else "application/octet-stream"
        data = file.read()
    else:
        raise ValueError("file_path 혹은 file 인자를 지정해주세요.")

    b64_str: str = b64encode(data).decode()
    url = f"data:{mime_type};base64," + b64_str
    return url
