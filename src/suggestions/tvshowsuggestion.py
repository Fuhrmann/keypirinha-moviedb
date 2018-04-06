import keypirinha_util as kpu
import json
from MovieDB import constants
from .mediasuggestion import MediaSuggestion
from .textsuggestion import TextSuggestion

class TVShowSuggestion(MediaSuggestion):

    def details_suggestions(self) -> list:
        """Returns all the suggestions used in this media details."""
        suggestions = [
            TextSuggestion(self.label, self._genres_text, self._id, self.icon),
            TextSuggestion(self._status, 'Status', 'tvshowstatus', 'Status'),
            self._get_year_suggestion(),
            self._get_seasons_suggestion()
        ]

        if self._omdb:
            suggestions.extend(self._get_ratings_suggestions())

        if self._main_cast:
            suggestions.extend(self._get_main_cast_suggestion())

        return suggestions

    def _get_seasons_suggestion(self) -> TextSuggestion:
        """Returns the suggestion representing the seasons detail."""
        label = '{} {}'.format(self._number_of_seasons, 'season' if self._number_of_seasons == 1 else 'seasons')
        description = 'Number of seasons'
        url = '{}/tv/{}/seasons'.format(constants.URL_MOVIEDB_BASE, self._id)
        target = kpu.kwargs_encode(url=url)
        return TextSuggestion(label, description, target, 'Seasons')

    def _get_year_suggestion(self):
        """Returns the suggestion representing the release year detail."""
        from .searchsuggestion import SearchSuggestion
        url = '{}/discover/{}?first_air_date_year={}'.format(constants.URL_MOVIEDB_BASE, self._media_type, self._year)
        target = kpu.kwargs_encode(url=url, media_type=self._media_type, search_args=json.dumps({'first_air_date_year': self._year}))
        return SearchSuggestion(self._year, 'Year', target, 'Calendar')

    @property
    def label(self) -> str:
        label = self._tmdb['name']
        if self._year:
            label += ' ({})'.format(self._year)

        return label

    @MediaSuggestion.description.getter
    def description(self) -> str:
        if self._description:
            return self._description

        description = 'popularity: {0:.2f}%'.format(self._popularity)
        if self._first_air_date:
            description += ' • release date: {}'.format(self._first_air_date)

        return description

    @property
    def icon(self) -> str:
        return 'TV'

    @property
    def _year(self) -> str:
        if self._first_air_date:
            return self._first_air_date[:4]

        if self._omdb:
            return self._omdb['year']

        return None

    @property
    def _last_air_date(self) -> str:
        return self._tmdb.get('last_air_date', None)

    @property
    def _first_air_date(self) -> str:
        if 'first_air_date' not in self._tmdb or self._tmdb['first_air_date'] is None:
            return 'N/A'

        return self._tmdb['first_air_date']

    @property
    def _number_of_seasons(self) -> str:
        return self._tmdb.get('number_of_seasons', None)

    @property
    def _overview(self) -> str:
        return self._tmdb.get('overview', None)

    @property
    def _status(self) -> str:
        return self._tmdb.get('status', None)

    @property
    def _media_type(self) -> str:
        return 'tv'
