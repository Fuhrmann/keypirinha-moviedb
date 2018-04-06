from keypirinha import ItemCategory
from .suggestion import Suggestion


class TextSuggestion(Suggestion):

    ITEM_CAT = ItemCategory.USER_BASE + 40

