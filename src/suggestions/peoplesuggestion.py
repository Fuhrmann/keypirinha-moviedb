from datetime import datetime
from .mediasuggestion import MediaSuggestion

class PeopleSuggestion(MediaSuggestion):

    def details_suggestions(self) -> list:
        """Returns all the suggestions used in this media details."""
        from .textsuggestion import TextSuggestion

        description = ''
        if self._birthday:
            description = '{} years'.format(self._age)

        suggestions = [
            TextSuggestion(self.label, description, self._id, self.icon),
        ]

        if self._know_as:
            suggestions.append(TextSuggestion(', '.join(self._know_as), 'Also know as', 'peopleknowas', 'KnowAs'))

        if self._birthday:
            suggestions.append(TextSuggestion(self._birthday, 'Born', 'peopleborn', 'Calendar'))

        if self._deathday:
            suggestions.append(TextSuggestion(self._deathday, 'Died', 'peopledied', 'Death'))

        if self._place_of_birth:
            suggestions.append(TextSuggestion(self._place_of_birth, 'Place of birth', 'peopleplacebirth', 'City'))

        if self._main_credits:
            suggestions.extend(self._get_credits_suggestion())

        return suggestions

    def _get_credits_suggestion(self) -> list:
        from .moviesuggestion import MovieSuggestion

        # TODO: Instead of only movie credits, show also tv credits
        rv = []
        for credit in self._main_credits:
            suggestion = MovieSuggestion(credit)
            suggestion.description = 'as {}'.format(credit['character'])
            rv.append(suggestion)

        return rv

    @property
    def label(self) -> str:
        return self._tmdb['name']

    @MediaSuggestion.description.getter
    def description(self) -> str:
        if self._description:
            return self._description

        return 'popularity: {0:.2f}%'.format(self._popularity)

    @MediaSuggestion.icon.getter
    def icon(self) -> str:
        if self._icon:
            return self._icon

        return self._gender_text.capitalize() if self._gender_text is not None else 'Person'

    @property
    def _birthday(self) -> str:
        return self._tmdb.get('birthday', None)

    @property
    def _deathday(self) -> str:
        return self._tmdb.get('deathday', None)

    @property
    def _age(self) -> int:
        if self._birthday:
            return int((datetime.today() - datetime.strptime(self._birthday, "%Y-%m-%d")).days / 365)

    @property
    def _place_of_birth(self) -> str:
        return self._tmdb.get('place_of_birth', None)

    @property
    def _popularity(self) -> str:
        return self._tmdb.get('popularity', None)

    @property
    def _gender(self):
        return self._tmdb.get('gender', None)

    @property
    def _gender_text(self) -> str:
        if not self._gender:
            return None

        return 'male' if self._gender == 2 else 'female'

    @property
    def _main_credits(self) -> list:
        combined_credits = self._combined_credits
        cast = combined_credits.get('cast', None)
        if credits is None or cast is None:
            return []

        return cast[:5]

    @property
    def _know_as(self) -> list:
        return self._tmdb.get('also_known_as', [])[:3]

    @property
    def _media_type(self) -> str:
        return 'person'
