class Suggestion(object):
    _label = None
    _description = None
    _target = None
    _icon = None
    _loop_on_suggest = None
    _data_bag = None

    def __init__(self, label=None, description=None, target=None, icon=None, loop_on_suggest=False, data_bag=None, category=None):
        self._label = str(label)
        self._description = str(description)
        self._target = target
        self._icon = icon
        self._loop_on_suggest = loop_on_suggest
        self._data_bag = data_bag
        self._category = category

    @property
    def label(self) -> str:
        return self._label

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value) -> str:
        self._description = value

    @property
    def target(self) -> str:
        return self._target

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value

    @property
    def loop_on_suggest(self) -> bool:
        return self._loop_on_suggest

    @property
    def data_bag(self) -> str:
        return self._data_bag

    @property
    def category(self) -> int:
        if hasattr(self, 'ITEM_CAT'):
            return self.ITEM_CAT

        return self._category

    def __str__(self) -> str:
        return 'Target: {}'.format(self.target)
