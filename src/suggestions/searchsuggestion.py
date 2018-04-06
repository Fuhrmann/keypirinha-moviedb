from keypirinha import ItemCategory
from .suggestion import Suggestion


class SearchSuggestion(Suggestion):

    ITEM_CAT = ItemCategory.USER_BASE + 10

    @property
    def loop_on_suggest(self) -> bool:
        return True

    @property
    def icon(self) -> str:
        if self._icon:
            return self._icon

        return 'Search'
