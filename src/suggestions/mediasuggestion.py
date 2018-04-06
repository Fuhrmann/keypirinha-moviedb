import keypirinha_util as kpu
from keypirinha import ItemCategory
from MovieDB import constants
from .suggestion import Suggestion
from .textsuggestion import TextSuggestion

class MediaSuggestion(Suggestion):

    ITEM_CAT = ItemCategory.USER_BASE + 20

    RATINGS_TYPE = {
        'Internet Movie Database': {'url': 'https://www.imdb.com/title/{}', 'info': 'imdb_id'},
        'Rotten Tomatoes': {'url': 'https://www.rottentomatoes.com/search/?search={}', 'info': '_title'},
        'Metacritic': {'url': 'https://www.metacritic.com/search/all/{}/results', 'info': '_title'},
    }

    def __init__(self, tmdb, *args, **kwargs):
        super(Suggestion, self).__init__(*args, **kwargs)
        self._tmdb = tmdb
        self._omdb = None

    def _get_ratings_suggestions(self) -> list:
        """
        Get the suggestion containing all the media's ratings.
        Currently the only place where this data come from is through OMDB api.
        """
        rv = []
        if self._ratings:
            for rating in self._ratings:
                rating_type = self.RATINGS_TYPE[rating['source']]
                info = getattr(self, rating_type['info'])
                search_url = rating_type['url'].format(info)
                target = kpu.kwargs_encode(url=search_url)
                rv.append(TextSuggestion(rating['value'], rating['source'], target, rating['source']))

        return rv

    def _get_main_cast_suggestion(self) -> list:
        from .peoplesuggestion import PeopleSuggestion
        rv = []
        for cast in self._main_cast:
            person = PeopleSuggestion(cast)
            person.description = 'as {}'.format(cast['character'])
            rv.append(person)

        return rv

    @property
    def target(self) -> str:
        url = '{}/{}/{}'.format(constants.URL_MOVIEDB_BASE, self._media_type, self._id)
        target = kpu.kwargs_encode(media_type=self._media_type, id=self._id, url=url)
        return target

    @property
    def loop_on_suggest(self) -> bool:
        return True

    @property
    def omdb(self) -> list:
        return self._omdb

    @omdb.setter
    def omdb(self, data):
        self._omdb = data

    @property
    def _id(self) -> str:
        return str(self._tmdb['id'])

    @property
    def _genres(self) -> list:
        return self._tmdb.get('genres', [])

    @property
    def _genres_text(self) -> str:
        return ', '.join([str(genre['name']) for genre in self._genres])

    @property
    def _popularity(self) -> str:
        return self._tmdb.get('popularity', None)

    @property
    def _trailer(self) -> dict:
        videos = self._videos
        trailer = list(
            filter(lambda video: video['type'] == 'Trailer', videos)
        )

        return {} if not trailer else trailer[0]

    @property
    def _ratings(self) -> list:
        return self._omdb.get('ratings', [])

    @property
    def imdb_id(self) -> str:
        imdb_id = self._tmdb.get('external_ids', {}).get('imdb_id', None)
        if imdb_id is None:
            imdb_id = self._tmdb.get('imdb_id', None)

        return imdb_id

    @property
    def _main_cast(self) -> list:
        credits = self._credits
        cast = credits.get('cast', None)

        if credits is None or cast is None:
            return []

        return cast[:5]

    @property
    def _credits(self) -> dict:
        return self._tmdb.get('credits', {})

    @property
    def _combined_credits(self) -> dict:
        return self._tmdb.get('combined_credits', {})

    @property
    def _videos(self) -> dict:
        return self._tmdb.get('videos', {}).get('results', {})

    @property
    def _media_type(self) -> str:
        return 'media'
