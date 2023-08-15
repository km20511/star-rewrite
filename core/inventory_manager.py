"""
게임 내 인벤토리를 관리하는 스크립트.
"""
from typing import Any, Callable, Dict, List, Optional, Set

from core.item import Item
from core.obj_data_formats import ItemData
from core.event_manager import EventManager
from core.utils import Comparable


class Inventory:
    """
    게임 속 플레이어가 보유하고 있는 아이템이 나열된 인벤토리.
    아이템을 관리하고, 효과 스크립트가 아이템에 접근할 수 있는 기능 제공.
    """
    def __init__(self, event_manager: EventManager, items: List[ItemData]) -> None:
        self.__event_manager: EventManager = event_manager
        self.__items: List[Item] = [Item(data).register_event(event_manager) for data in items]

    def get_items(self, query: Optional[Callable[[Item], bool]] = None) -> List[Item]:
        """조건에 맞는 아이템의 목록을 반환."""
        return list(filter(query, self.__items)) if query is not None else self.__items.copy()

    def add_item(self, item: ItemData):
        """목록의 맨 끝에 아이템 추가."""
        self.__items.append(Item(item))

    def get_readable_static_table(self) -> Dict[str, Any]:
        """효과 스크립팅에서 사용 가능한 정적 변수/함수 목록 반환(읽기 전용)."""
        return {
            "count_items": lambda query: len(self.get_items(query))
        }

    def get_writable_static_table(self, inventory_query: "InventoryQuery") -> Dict[str, Any]:
        """효과 스크립팅에서 사용 가능한 정적 변수/함수 목록 반환(쓰기 전용)."""
        return {
            "destroy_items": lambda : self.destroy_items(inventory_query)
        }
    
    def create_query(self) -> "InventoryQuery":
        """이 객체를 대상으로 하는 InventoryQuery 생성."""
        return InventoryQuery(self)
    
    def destroy_items(self, query: "InventoryQuery"):
        """조건에 맞는 아이템을 파괴. 사용에 해당하지 않음."""
        target_ids: Set[int] = query.get_target_from(self.__items)
        result: List[Item] = self.__items.copy()
        for item in self.__items:
            if item.id in target_ids:
                result.remove(item)
                self.__event_manager.on_item_destroyed(item)
        self.__items = result


class InventoryQuery:
    """
    인벤토리의 아이템을 선택하는 조건을 관리.
    직접 객체를 생성하기보다 Inventory.create_query()를 호출하는 것을 권장.
    """
    def __init__(self, inventory: Inventory) -> None:
        """
        InventoryQuery의 초기화 함수.
        직접 객체를 생성하기보다 Inventory.create_query()를 사용하는 것을 권장.
        :param inventory: Query를 적용할 인벤토리.
        """
        self.__inventory: Inventory = inventory
        self.__query: Optional[Callable[[Item], bool]] = None
        self.__order_method: Optional[Callable[[Item], Comparable]] = None
        self.__order_crop: int = -1
    
    def set_query(self, query: Callable[[Item], bool]) -> "InventoryQuery":
        """
        아이템을 검사할 조건을 추가.
        :param query: 추가할 조건. Item을 인수로 받아 bool을 반환해야 함.
        :return: chaining 구현을 위해 자기 자신 반환.
        """
        self.__query = query
        return self
    
    def set_order(self, order_method: Callable[[Item], Comparable], order_crop: int) -> "InventoryQuery":
        """
        아이템을 상위 몇 개까지 걸러내는 형태의 조건 추가.
        :param order_method: 정렬 기준. Item을 인수로 받아 비교 가능한 객체(sorted의 key와 동일)를 반환해야 함. 효과 적용 순서와는 무관.
        :param order_crop: 정렬된 대상을 상위 몇 개까지 선택할지 결정. 자연수가 아닌 경우 조건 추가가 이루어지지 않음.
        :return: chaining 구현을 위해 자기 자신 반환.
        """
        if order_crop > 0:
            self.__order_method = order_method
            self.__order_crop = order_crop
        return self

    def get_target_from(self, items: List[Item]) -> Set[int]:
        """
        주어진 목록에서 지정한 조건을 전부 만족하는 아이템 집합을 반환.
        :return: 조건을 만족하는 아이템의 id 집합.
        """
        if self.__query is not None:
            items = list(filter(self.__query, items))
        if self.__order_method is not None and self.__order_crop > 0:
            items = sorted(items, key=self.__order_method)[:self.__order_crop]
        return {item.id for item in items}

    def get_target(self) -> Set[int]:
        """
        지정한 조건을 전부 만족하는 덱의 아이템 집합을 반환.
        :return: 조건을 만족하는 아이템의 id 집합.
        """
        items: List[Item] = self.__inventory.get_items(self.__query) 
        if self.__order_method is not None and self.__order_crop > 0:
            items = sorted(items, key=self.__order_method)[:self.__order_crop]
        return {item.id for item in items}
