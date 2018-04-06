from .suggestions.searchsuggestion import SearchSuggestion
from .suggestions.moviesuggestion import MovieSuggestion
from .suggestions.tvshowsuggestion import TVShowSuggestion
from .suggestions.peoplesuggestion import PeopleSuggestion
from .suggestions.mediasuggestion import MediaSuggestion
from .suggestions.textsuggestion import TextSuggestion

SUPPORTED_MEDIA_TYPES = {'movie': 'Movies', 'tv': 'TV', 'people': 'People', 'person': 'People'}

SUGGESTIONS = {
    'movie': MovieSuggestion,
    'tv': TVShowSuggestion,
    'people': PeopleSuggestion,
    'person': PeopleSuggestion
}

URL_YOUTUBE_WATCH = 'https://youtube.com/watch?v={}'
URL_MOVIEDB_BASE = 'https://www.themoviedb.org'
