"""GUI 모듈에서 사용하는 유용한 기능을 모아 둔 스크립트."""
from pyglet.math import Vec2, Mat3

def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """value를 minimum과 maximum 사이의 값으로 제한하는 함수(float)."""
    return minimum if value < minimum else (maximum if value > maximum else value)

def lerp(a: float, b: float, t: float) -> float:
    """a와 b 사이를 t : 1-t로 내분하는 실수를 계산하는 선형 보간 함수.
    0 <= t <= 1이어야 함."""
    return (b-a)*clamp(t) + a

def trs_matrix(t: Vec2, r: float, s: Vec2) -> Mat3:
    """주어진 인수를 이용해 TRS 행렬을 생성함."""
    tr_mat: Mat3 = Mat3((
        1.0, 0.0, 0.0, # 1열
        0.0, 1.0, 0.0, # 2열
        t.x, t.y, 1.0  # 3열
    )).rotate(r)
    s_mat: Mat3 = Mat3((
        s.x, 0.0, 0.0,
        0.0, s.y, 0.0,
        0.0, 0.0, 1.0
    ))
    return tr_mat @ s_mat