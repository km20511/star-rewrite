from core.effect import Effect, EffectHolder
from core.card_data_manager import ItemData


class Item(EffectHolder):
    """
    인벤토리에 존재하는 아이템 클래스.
    """
    def __init__(self, data: ItemData) -> None:
        self.__item_data: ItemData = data
        super().__init__([Effect(self, effect_data) for effect_data in data.effects])

    @property
    def item_data(self):
        return self.__item_data