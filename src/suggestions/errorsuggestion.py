from .suggestion import Suggestion

class ErrorSuggestion(Suggestion):

    @property
    def icon(self) -> str:
        return None