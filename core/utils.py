""" core 모듈 내 스크립트가 사용하는 작은 기능들을 모아 둔 스크립트. """

from typing import Protocol, TypeVar


_T_contra = TypeVar("_T_contra", contravariant=True)


class Comparable(Protocol[_T_contra]):
    """비교 가능한 자료형의 타이핑 지원 클래스. sorted의 내부 타이핑 선언 모방."""
    def __lt__(self, other: _T_contra) -> bool:
        pass
    def __gt__(self, other: _T_contra) -> bool:
        pass
