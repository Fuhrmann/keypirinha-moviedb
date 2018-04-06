import keypirinha_util as kpu
import json
from MovieDB import constants
from .mediasuggestion import MediaSuggestion

class MovieSuggestion(MediaSuggestion):

    def details_suggestions(self) -> list:
        """Returns all the suggestions used in this media details."""
        from .peoplesuggestion import PeopleSuggestion
        from .textsuggestion import TextSuggestion

        suggestions = [
            TextSuggestion(self.label, self._genres_text, self._id, self.icon),
            self._get_year_suggestion(),
            TextSuggestion(self._runtime, 'Runtime', 'movieruntime', 'Clock')
        ]

        if self._director:
            director = PeopleSuggestion(self._director)
            director.description = 'Director'
            director.icon = 'Director'
            suggestions.append(director)

        if self._tagline:
            suggestions.append(TextSuggestion(self._tagline, 'Tagline', 'movietagline', 'Tagline'))

        if self._omdb:
            suggestions.extend(self._get_ratings_suggestions())

        if self._trailer:
            suggestions.append(
                TextSuggestion(
                    'Trailer',
                    "Watch trailer on {}".format(self._trailer['site']),
                    kpu.kwargs_encode(url=constants.URL_YOUTUBE_WATCH.format(self._trailer['key'])),
                    'Trailer'
                )
            )

        if self._main_cast:
            suggestions.extend(self._get_main_cast_suggestion())

        return suggestions

    def _get_year_suggestion(self):
        """Returns the suggestion representing the release year detail."""
        from .searchsuggestion import SearchSuggestion
        url = '{}/discover/{}?primary_release_year={}'.format(constants.URL_MOVIEDB_BASE, self._media_type, self._year)
        target = kpu.kwargs_encode(url=url, media_type=self._media_type, search_args=json.dumps({'primary_release_year': self._year}))
        return SearchSuggestion(self._year, 'Year', target, 'Calendar')

    @property
    def label(self) -> str:
        label = self._title
        if self._year:
            label += ' ({})'.format(self._year)

        return label

    @MediaSuggestion.description.getter
    def description(self) -> str:
        if self._description:
            return self._description

        description = 'popularity: {0:.2f}%'.format(self._popularity)
        if self._release_date:
            description += ' • release date: {}'.format(self._release_date)

        return description

    @property
    def icon(self) -> str:
        return 'Movies'

    @property
    def _title(self) -> str:
        return self._tmdb.get('title', None)

    @property
    def _year(self) -> str:
        if self._release_date:
            return self._release_date[:4]

        if self._omdb:
            return self._omdb['year']

        return 'N/A'

    @property
    def _tagline(self) -> str:
        return self._tmdb.get('tagline', None)

    @property
    def _release_date(self) -> str:
        return self._tmdb.get('release_date', None)

    @property
    def _runtime(self) -> str:
        runtime = self._tmdb.get('runtime', None)
        if not runtime and self._omdb:
            runtime = self._omdb.get('runtime', None)

        return '{} min'.format(runtime) if runtime else 'N/A'

    @property
    def _director(self) -> list:
        credits = self._credits
        crew = credits.get('crew', [])
        director = list(
            filter(lambda people: people['department'] == 'Directing', crew)
        )

        return None if not director else director[0]

    @property
    def _media_type(self) -> str:
        return 'movie'
