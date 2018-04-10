import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import json
import keypirinha as kp
import keypirinha_util as kpu
import tmdbsimple as tmdb
import omdb
import re
import requests_cache
from MovieDB import constants
from .suggestions.searchsuggestion import SearchSuggestion
from .suggestions.mediasuggestion import MediaSuggestion
from .suggestions.errorsuggestion import ErrorSuggestion
from .suggestions.suggestion import Suggestion
from .userinputparser import UserInputParser


class Suggester:
    ITEM_CAT_MORE = kp.ItemCategory.USER_BASE + 30

    def __init__(self, settings, icons, cache_path):
        self.input_parser = UserInputParser()
        self.settings = settings
        self.icons = icons
        self.cache_path = cache_path
        self.user_input = None
        self.current_suggestions = None
        self.current_page = 1
        self.total_pages = 1
        self._configure_keys()

    def with_input(self, selected_chain, original_user_input):
        """Suggest when there is an query entered by the user"""
        selected_category, selected_target, user_input = self._parse_selections(selected_chain, original_user_input)

        match_type = kp.Match.ANY

        # If the selected category is equal to a search preset and we already
        # have suggestions loaded, keep it and change the current match_type to FUZZY,
        # so the user can filter the current suggestions without loading anything new from the API
        if selected_category == SearchSuggestion.ITEM_CAT and self.current_suggestions:
            suggestions = self.current_suggestions
            match_type = kp.Match.FUZZY
        elif selected_category == kp.ItemCategory.KEYWORD:
            search_config = self.input_parser.parse(user_input, selected_target[
                'media_type'] if 'media_type' in selected_target else selected_target)

            # At this point we already know that the selected category is a keyword
            # So what we're doing now is to find out if the current page is not the first one.
            # If this condition is met, it means the user already requested to load the next page.
            # Which means: any typed word will be match against the current suggestions using the FUZZY match type
            if self.current_page > 1 and self.user_input != original_user_input:
                suggestions = self.current_suggestions
                match_type = kp.Match.FUZZY
            elif search_config:
                # In this case we know that the user is trying to search for
                # media using one of the supported query searches: year:2001, genre:action
                if kp.should_terminate(0.85):
                    return None, match_type

                suggestions = self._execute_search_preset(search_config)
            else:
                # And finally, this is the case when we'll search for media matching the entered query by the user
                if kp.should_terminate(0.55):
                    return None, match_type

                suggestions = self._search(user_input, selected_target)

            self.user_input = user_input
        else:
            # This part only occurs when the user requested to see
            # the media details. In this case, we already have the media
            # details and the user will be able to filter out anything using the
            # FUZZY match type. This means: anything entered in the searchbox will be
            # scored against the media details suggestions. This is done by keypirinha's.
            suggestions = self.current_suggestions
            match_type = kp.Match.FUZZY

        self.current_suggestions = suggestions

        return self._append_load_more(suggestions), match_type

    def without_input(self, selected_chain):
        """Suggest when there is no query"""
        selected_category, selected_target, user_input = self._parse_selections(selected_chain)
        match_type = kp.Match.ANY

        suggestions = []
        if user_input:
            return self.with_input(selected_chain, user_input)

        # If the user did not typed anything at all, we'll suggest the search presets
        if selected_category == kp.ItemCategory.KEYWORD:
            suggestions = self._list_search_presets(selected_target)

        # Execute the search preset
        if selected_category == SearchSuggestion.ITEM_CAT:
            suggestions = self._execute_search_preset(selected_target)

        # Get media's details
        if selected_category == MediaSuggestion.ITEM_CAT:
            suggestions = self._get_media_detail(selected_target['id'], selected_target['media_type'])

        self.current_suggestions = suggestions

        return self._append_load_more(suggestions), match_type

    def _list_search_presets(self, media_type) -> list:
        """Lists all the defined search presets, if there it is any."""
        suggestions = []
        if media_type in self.settings['search_presets']:
            presets = self.settings['search_presets'][media_type]
            for preset_name, preset in presets.items():
                suggestions.append(preset)

        # Just to be sure
        self.current_page = 1
        self.total_pages = 1

        return suggestions

    def _execute_search_preset(self, search_config) -> list:
        """Given an search preset, execute it."""
        try:
            media_type = search_config['media_type']
            discover = tmdb.Discover()
            search_args = json.loads(search_config['search_args'])

            # if the user wants to search by genre, we need to get the genre's ids first
            if 'with_genres' in search_args:
                search_args['with_genres'] = self._get_genres_id(search_args['with_genres'], media_type)

            search_args['page'] = self.current_page
            search_args['language'] = self.settings['language']
            results = getattr(discover, media_type)(**search_args)  # discover.tv(), discover.movie()

            total_pages = 1
            if 'total_pages' in results:
                total_pages = results['total_pages']

            return self._create_suggestions(results['results'], total_pages, media_type)
        except tmdb.base.APIKeyError as exc:
            print(exc)
            return [ErrorSuggestion('TMDB API key not configured/invalid!', 'No results found')]
        except Exception as exc:
            print(exc)
            return [ErrorSuggestion('There was an error trying to connect to TMDB API.', 'No results found')]

    def _search(self, user_input, media_type) -> list:
        """Search for movies/tv shows/people using the query entered by the user."""
        try:
            search = tmdb.Search()
            # self.tmdb.movie(), self.tmdb.tv() or self.tmdb.people() <- renamed to person
            func = getattr(search, media_type)
            func(query=user_input, page=self.current_page, language=self.settings['language'])

            return self._create_suggestions(search.results, search.total_pages, media_type)
        except Exception as exc:
            print(exc)
            return [ErrorSuggestion('There was an error trying to connect to TMDB API.', 'No results found')]

    def _create_suggestions(self, results, total_pages, media_type) -> list:
        """Given a list of results, iterate it and create the suggestions items."""
        suggestions = []
        self.total_pages = total_pages

        for item in results:
            suggestion = constants.SUGGESTIONS[media_type](item)
            try:
                suggestions.append(suggestion)
            except Exception as exc:
                print(exc)
                print('There was an error creating the suggestion {}: {}'.format(suggestion, exc))
                continue

        return suggestions

    def _get_media_detail(self, tmdb_id, media_type) -> list:
        """Search the details of a specific media, it could be movies/tv show/person."""
        media_type_class = constants.SUPPORTED_MEDIA_TYPES[media_type]
        search = getattr(tmdb, media_type_class)(tmdb_id)  # self.tmdb.Movie, self.tmdb.TV or self.tmdb.People

        tmdb_data = search.info(append_to_response='videos,external_ids,credits,combined_credits',
                                language=self.settings['language'])
        suggestion = constants.SUGGESTIONS[media_type](tmdb_data)

        # Not every movie/tvshow has omdb data
        imdb_id = suggestion.imdb_id
        if imdb_id:
            # Don't call omdb for people details
            if not imdb_id.startswith('nm'):
                try:
                    omdb_data = omdb.imdbid(imdb_id)
                except Exception:
                    omdb_data = None

                if omdb_data and 'response' in omdb_data and omdb_data['response'] == 'True':
                    suggestion.omdb = omdb_data

        suggestions = []
        for item in suggestion.details_suggestions():
            try:
                suggestions.append(item)
            except Exception as exc:
                print('There was an error creating the suggestion {}: {}'.format(item, exc))
                continue

        # Just to be sure
        self.total_pages = 1
        self.current_page = 1

        return suggestions

    def _configure_keys(self):
        """Configures the API services with the keys provided in the settings."""
        tmdb.API_KEY = self.settings['tmdb_api_key']
        tmdb.SESSION = requests_cache.CachedSession(os.path.join(self.cache_path, 'requests'), backend='filesystem',
                                                    expire_after=self.settings['cache_expire_after'])
        omdb.set_default('apikey', self.settings['omdb_api_key'])
        omdb.set_default('timeout', 5)

    def _parse_selections(self, selected_chain, user_input=None):
        if selected_chain.category() == self.ITEM_CAT_MORE:
            self.current_page = int(selected_chain.target())
            selected_chain = self.last_selected_chain
            # if the last selected chain was a keyword, lets bring back the input
            if selected_chain.category() == kp.ItemCategory.KEYWORD:
                user_input = self.user_input
        else:
            self.current_page = 1
            self.last_selected_chain = selected_chain

        selected_category = selected_chain.category()
        selected_target = self._parse_selected_target(selected_chain)

        return selected_category, selected_target, user_input

    def _parse_selected_target(self, selected_chain):
        try:
            selected_target = kpu.kwargs_decode(selected_chain.target())
        except Exception:
            selected_target = selected_chain.target()

        return selected_target

    def _append_load_more(self, suggestions):
        """Append the 'Load more' suggestion if it is necessary."""
        # The user is able to navigate the pages since the tmdb api only returns 20 items
        # This suggestion only appears if there is more pages to load
        if self.total_pages > self.current_page:
            next_page = self.current_page + 1
            suggestions.append(Suggestion(
                'Load more...',
                'Go to page {} of {}'.format(next_page, self.total_pages),
                str(next_page),
                'NextPage',
                True,
                None,
                self.ITEM_CAT_MORE,
            ))

        return suggestions

    def _get_genres_id(self, value, media_type):
        """Given an list of genres names, discover their ids."""
        method_name = 'tv_list'
        if media_type == 'movie':
            method_name = 'movie_list'

        genres = getattr(tmdb.Genres(), method_name)()
        value = value.split(',')

        ids = []
        regex = re.compile('[\s+&-]', re.IGNORECASE)
        for genre in genres['genres']:
            genre_name = regex.sub('', genre['name'].lower())
            if genre_name in value:
                ids.append(str(genre['id']))

        # If the genre entered by the user was'nt found, we append a zero so
        # the results from the API will be null
        if not ids:
            ids.append(str(0))

        return ','.join(ids)
