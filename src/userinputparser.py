import re
import json

class UserInputParser:

    SUPPORTED_FILTERS = {
        'genre': 'with_genres',
        'year': {'movie': 'primary_release_year', 'tv': 'first_air_date_year'},
        'lang': 'with_original_language',
        'sort': 'sort_by',
        'votes': 'vote_count',
        'runtime': 'with_runtime'
    }

    # filter:(< or >)value(.asc or .desc)
    DEFAULT_REGEX_PARSER = '(\w+):([<>]?)([\w.,|]+)'

    def parse(self, user_input, media_type):
        """Parse the user_input and check if there is a word that matches one of the filters above"""
        if media_type == 'people' or media_type == 'person':
            return None

        queries = re.finditer(self.DEFAULT_REGEX_PARSER, user_input)
        search_args = {}
        for query in queries:
            filter_type = query.group(1)
            symbol = query.group(2)
            value = query.group(3)

            # If the filter entered by the user is not current supported, go to the next
            if filter_type not in self.SUPPORTED_FILTERS.keys():
                continue

            field_name = self.SUPPORTED_FILTERS[filter_type]
            if symbol:
                condition = '.lte' if symbol == '<' else '.gte'
                field_name += condition

            # This means the field from the search differs from media_type, so we should get it
            if isinstance(field_name, dict):
                field_name = field_name[media_type]

            search_args[field_name] = value.strip(' ').lower()

        if not search_args:
            return None

        search_config = {}
        search_config['media_type'] = media_type
        search_config['search_args'] = json.dumps(search_args)

        return search_config
