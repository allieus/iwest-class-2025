"""
Structured Output 기능 테스트

OpenAI의 Structured Output을 사용하여 Pydantic 모델 기반 응답을 테스트합니다.
"""

import os
from pydantic import BaseModel
from utils import make_response, ResponseWithUsage, StructuredResponseWithUsage


# 테스트용 Pydantic 모델들
class UserInfo(BaseModel):
    """사용자 정보 모델"""
    name: str
    age: int
    email: str | None = None


class ProductReview(BaseModel):
    """상품 리뷰 분석 모델"""
    rating: int  # 1-5
    sentiment: str  # positive, negative, neutral
    keywords: list[str]
    summary: str


class MathProblem(BaseModel):
    """수학 문제 풀이 모델"""
    class Step(BaseModel):
        explanation: str
        result: str
    
    problem: str
    steps: list[Step]
    final_answer: str


class CompanyAnalysis(BaseModel):
    """회사 분석 모델 (복잡한 중첩 구조)"""
    class Department(BaseModel):
        name: str
        employee_count: int
        budget: float | None = None
    
    company_name: str
    industry: str
    departments: list[Department]
    total_employees: int
    is_public: bool


def test_basic_structured_output():
    """기본적인 구조화된 출력 테스트"""
    print("\n=== 기본 Structured Output 테스트 ===")
    
    # UserInfo 모델 테스트
    response = make_response(
        "Extract user information: John Doe is 30 years old and his email is john@example.com",
        response_format=UserInfo,
    )
    
    # 타입 확인
    assert isinstance(response, StructuredResponseWithUsage)
    assert isinstance(response.parsed, UserInfo)
    
    # 값 확인
    print(f"이름: {response.parsed.name}")
    print(f"나이: {response.parsed.age}")
    print(f"이메일: {response.parsed.email}")
    
    # Usage 정보 확인
    if response.usage:
        print(f"입력 토큰: {response.usage.input_tokens}")
        print(f"출력 토큰: {response.usage.output_tokens}")
        print(f"전체 토큰: {response.usage.total_tokens}")
    
    print("✅ 기본 테스트 통과")


def test_backward_compatibility():
    """기존 기능과의 호환성 테스트"""
    print("\n=== 호환성 테스트 ===")
    
    # response_format 없이 호출
    response = make_response("안녕하세요, 오늘 날씨가 좋네요!")
    
    # 타입 확인
    assert isinstance(response, ResponseWithUsage)
    assert isinstance(response, str)  # 문자열처럼 동작
    
    # 문자열 연산 테스트
    print(f"응답: {response}")
    print(f"응답 길이: {len(response)}")
    
    # Usage 정보 확인
    if response.usage:
        print(f"전체 토큰: {response.usage.total_tokens}")
    
    print("✅ 호환성 테스트 통과")


def test_complex_model():
    """복잡한 모델 테스트"""
    print("\n=== 복잡한 모델 테스트 ===")
    
    # 리뷰 분석
    review_response = make_response(
        "Review: This product is amazing! Great quality, fast shipping, and excellent customer service. "
        "The only minor issue was the packaging, but overall I'm very satisfied. 5 stars!",
        response_format=ProductReview,
    )
    
    print(f"평점: {review_response.parsed.rating}/5")
    print(f"감정: {review_response.parsed.sentiment}")
    print(f"키워드: {', '.join(review_response.parsed.keywords)}")
    print(f"요약: {review_response.parsed.summary}")
    
    print("✅ 복잡한 모델 테스트 통과")


def test_nested_model():
    """중첩된 모델 테스트"""
    print("\n=== 중첩 모델 테스트 ===")
    
    company_response = make_response(
        "TechCorp is a software company with 3 departments: "
        "Engineering (50 employees, $5M budget), "
        "Sales (20 employees, $2M budget), and "
        "HR (10 employees). "
        "Total 80 employees. It's a public company.",
        response_format=CompanyAnalysis,
    )
    
    print(f"회사명: {company_response.parsed.company_name}")
    print(f"산업: {company_response.parsed.industry}")
    print(f"상장 여부: {company_response.parsed.is_public}")
    print(f"총 직원수: {company_response.parsed.total_employees}")
    
    print("\n부서 정보:")
    for dept in company_response.parsed.departments:
        budget_str = f"${dept.budget}M" if dept.budget else "미정"
        print(f"  - {dept.name}: {dept.employee_count}명, 예산 {budget_str}")
    
    print("✅ 중첩 모델 테스트 통과")


def test_math_problem():
    """수학 문제 풀이 테스트"""
    print("\n=== 수학 문제 풀이 테스트 ===")
    
    math_response = make_response(
        "Solve step by step: If a train travels 120 km in 2 hours, "
        "how far will it travel in 5 hours at the same speed?",
        response_format=MathProblem,
    )
    
    print(f"문제: {math_response.parsed.problem}")
    print("\n풀이 단계:")
    for i, step in enumerate(math_response.parsed.steps, 1):
        print(f"  {i}. {step.explanation}")
        print(f"     → {step.result}")
    
    print(f"\n최종 답: {math_response.parsed.final_answer}")
    
    print("✅ 수학 문제 테스트 통과")


def test_korean_content():
    """한글 콘텐츠 테스트"""
    print("\n=== 한글 콘텐츠 테스트 ===")
    
    response = make_response(
        "다음 정보를 추출해주세요: 김철수씨는 35살이고 이메일은 kim@example.kr입니다.",
        response_format=UserInfo,
        system_content="응답은 반드시 한글로 해주세요.",
    )
    
    print(f"이름: {response.parsed.name}")
    print(f"나이: {response.parsed.age}")
    print(f"이메일: {response.parsed.email}")
    
    print("✅ 한글 테스트 통과")


def test_with_system_prompt():
    """시스템 프롬프트와 함께 테스트"""
    print("\n=== 시스템 프롬프트 테스트 ===")
    
    response = make_response(
        "이 제품은 정말 최고입니다! 배송도 빠르고 품질도 훌륭해요.",
        response_format=ProductReview,
        system_content="You are a professional product review analyzer. Always provide detailed and accurate analysis.",
    )
    
    print(f"평점: {response.parsed.rating}/5")
    print(f"감정: {response.parsed.sentiment}")
    print(f"키워드: {response.parsed.keywords}")
    
    print("✅ 시스템 프롬프트 테스트 통과")


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 50)
    print("Structured Output 테스트 시작")
    print("=" * 50)
    
    try:
        # 기본 테스트
        test_basic_structured_output()
        
        # 호환성 테스트
        test_backward_compatibility()
        
        # 복잡한 모델 테스트
        test_complex_model()
        
        # 중첩 모델 테스트
        test_nested_model()
        
        # 수학 문제 테스트
        test_math_problem()
        
        # 한글 콘텐츠 테스트
        test_korean_content()
        
        # 시스템 프롬프트 테스트
        test_with_system_prompt()
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 통과!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise


if __name__ == "__main__":
    # OpenAI API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY 환경 변수를 설정해주세요.")
        exit(1)
    
    run_all_tests()