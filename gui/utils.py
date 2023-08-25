"""GUI 모듈에서 사용하는 유용한 기능을 모아 둔 스크립트."""

def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """value를 minimum과 maximum 사이의 값으로 제한하는 함수(float)."""
    return minimum if value < minimum else (maximum if value > maximum else value)

def lerp(a: float, b: float, t: float) -> float:
    """a와 b 사이를 t : 1-t로 내분하는 실수를 계산하는 선형 보간 함수.
    0 <= t <= 1이어야 함."""
    return (b-a)*clamp(t) + a
