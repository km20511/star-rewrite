from pyglet.math import Vec2, Mat3

from gui.utils import lerp, trs_matrix

class Transform2D:
    """변위, 회전, 크기를 이용해 좌표계 변환을 수행할 수 있는 객체."""
    def __init__(self, pos: Vec2, rot: float, scale: Vec2) -> None:
        self.__pos = pos
        self.__rot = rot
        self.__scale = scale
        self._calc_matrix()

    @property
    def position(self) -> Vec2:
        return self.__pos
    
    @position.setter
    def position(self, val: Vec2) -> None:
        self.__pos = val
        self._calc_matrix()

    @property
    def rotation(self) -> float:
        return self.__rot
    
    @rotation.setter
    def rotation(self, val: float) -> None:
        self.__rot = val
        self._calc_matrix()

    @property
    def scale(self) -> Vec2:
        return self.__scale
    
    @scale.setter
    def scale(self, val: Vec2) -> None:
        self.__scale = val
        self._calc_matrix()

    def _calc_matrix(self) -> None:
        self.__mat = trs_matrix(self.__pos, self.__rot, self.__scale)

    @property
    def matrix(self) -> Mat3:
        return self.__mat
    
    @staticmethod
    def lerp(a: "Transform2D", b: "Transform2D", t: float) -> "Transform2D":
        p: Vec2 = Vec2(lerp(a.__pos.x, b.__pos.x, t), lerp(a.__pos.y, b.__pos.y, t))
        r: float = lerp(a.__rot, b.__rot, t)
        s: Vec2 = Vec2(lerp(a.__scale.x, b.__scale.x, t), lerp(a.__scale.y, b.__scale.y, t))
        return Transform2D(p, r, s)