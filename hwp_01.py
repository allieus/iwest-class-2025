import os
import subprocess


def find_업무분장_hwp_files(base_path: str) -> list[str]:
    """
    지정 경로 내의 모든 하위 디렉토리에서
    업무 문장 HWP 파일의 경로를 찾아서
    리스트로 반환합니다.
    """
    hwp_files = []
    for root, __, files in os.walk(base_path):
        for filename in files:
            # FIXME: 파일명 인코딩 이슈인지 macOS에서 "업무분장" in filename 에서 False 판정
            if "업무분장" in filename and filename.endswith(".hwp"):
                # if filename.endswith(".hwp"):
                hwp_files.append(os.path.join(root, filename))
    return hwp_files


def run_convert_cmd(hwp_path: str) -> str:
    output_path = os.path.splitext(hwp_path)[0] + ".html"
    cmd = [
        "hwp5html",
        "--html",
        "--output",
        output_path,
        hwp_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # 대개의 경우, 인자 구성이 잘못되었을 때 에러가 발생할 겁니다.
    if result.returncode != 0:  # 프로그램의 종료 코드
        raise RuntimeError(f"변환 오류 : {result.stderr}")

    return output_path


def main():
    hwp_files = find_업무분장_hwp_files(".")
    for hwp_path in hwp_files:
        html_path = run_convert_cmd(hwp_path)
        print("Created", html_path)


main()
