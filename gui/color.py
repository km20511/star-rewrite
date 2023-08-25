from typing import Tuple
from gui.utils import clamp


class Color:
    """[0, 1] 사이의 성분을 갖는 색 클래스.
    덧셈, 뺄셈, 스칼라 곱/나눗셈 지원.
    주의: 연산마다 범위를 검사하지 않으므로, 적절할 때 clamp()를 호출할 것."""
    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 0.0) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.clamp()

    def clamp(self) -> "Color":
        """각 성분을 [0, 1] 사이의 값으로 제한."""
        self.r = clamp(self.r)
        self.g = clamp(self.g)
        self.b = clamp(self.b)
        self.a = clamp(self.a)
        return self

    def tuple(self) -> Tuple[float, float, float, float]:
        """Tuple로 변환."""
        return self.r, self.g, self.b, self.a

    def tuple_256(self) -> Tuple[int, int, int, int]:
        """[0, 255] 사이의 정수 성분의 Tuple로 변환."""
        return int(self.r * 255), int(self.g * 255), int(self.b * 255), int(self.a * 255)

    def __add__(self, other: "Color"):
        return Color(
            self.r + other.r,
            self.g + other.g,
            self.b + other.b,
            self.a + other.a
        )

    def __sub__(self, other: "Color"):
        return Color(
            self.r - other.r,
            self.g - other.g,
            self.b - other.b,
            self.a - other.a
        )

    def __mul__(self, other: float):
        return Color(
            self.r * other,
            self.g * other,
            self.b * other,
            self.a * other
        )

    def __div__(self, other: float):
        return Color(
            self.r / other,
            self.g / other,
            self.b / other,
            self.a / other
        )