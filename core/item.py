from . import effect
from . import card_data_manager as cdm


class Item(effect.EffectHolder):
    """
    인벤토리에 존재하는 아이템 클래스.
    """
    def __init__(self, data: cdm.ItemData) -> None:
        self.__item_data: cdm.ItemData = data
        super().__init__([effect.Effect.from_json_dict(self, tree) for tree in data.effects])

    @property
    def item_data(self):
        return self.__item_data