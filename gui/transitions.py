from typing import Callable, TypeVar, Generic, Protocol

from gui.utils import clamp

class Transitionable(Protocol):
    def __add__(self, other):
        pass
    def __sub__(self, other):
        pass
    def __mul__(self, other: float):
        pass

_T_Transitionable = TypeVar("_T_Transitionable", bound=Transitionable)

def ease_out_expo(t: float) -> float:
    """지수함수를 이용한 ease out 전이 함수.
    인수 및 반환값 모두 닫힌구간 [0, 1] 안에 존재."""
    t = clamp(t)
    if 1.0 - t <= 0.001:
        return 1.0
    return 1.0 - 2 ** (-10 * t)

class Transition(Generic[_T_Transitionable]):
    """한 상태에서 다른 상태로의 전이를 수행."""
    def __init__(
            self, 
            start: _T_Transitionable, 
            destination: _T_Transitionable, 
            duration: float = -1,
            method: Callable[[float], float] = ease_out_expo
            ) -> None:
        self.start_value: _T_Transitionable = start
        self.current_value: _T_Transitionable = start
        self.destination_value: _T_Transitionable = destination
        self.method: Callable[[float], float] = method
        self.active: bool = False
        if duration >= 0:
            self._duration: float = duration
        self._started_time: float = -1.0

    def _lerp(self, a: _T_Transitionable, b: _T_Transitionable, t: float) -> _T_Transitionable:
        """전용 선형 보간 함수."""
        return (b-a)*t + a

    def start(self, current_time: float, duration: float = -1, reset: bool = True):
        """주어진 시간을 토대로 전이를 실행.
        reset이 참이라면 현재 값을 시작 값으로 덮어씀."""
        if self.active: return
        if reset:
            self.current_value = self.start_value
        if duration >= 0:
            self._duration = duration
        assert self._duration >= 0, "전이 기간은 0 이상의 float 값으로 설정되어야 합니다."
        self._started_time = current_time
        self.active = True

    def update(self, current_time: float) -> _T_Transitionable:
        """주어진 시간을 기반으로 현재 상태를 갱신하고 값을 반환."""
        if current_time >= self._started_time + self._duration:
            self.end()
            return self.destination_value
        self.current_value = self._lerp(
            self.start_value, 
            self.destination_value, 
            self.method((current_time - self._started_time) / self._duration)
        )
        return self.current_value
            
    def end(self, correct_value: bool = True):
        """전이를 완료함. correct_value가 참이면 현재 값을 목표 값으로 지정."""
        if correct_value:
            self.current_value = self.destination_value
        self.active = False
