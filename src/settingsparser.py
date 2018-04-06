import keypirinha_util as kpu
import json
from MovieDB import constants
from .suggestions.searchsuggestion import SearchSuggestion

class SettingsParser:
    """
    Parse the settings used by this plugin.
    The main purpose of this file is to parse the default search presets and the ones defined by the user.
    """
    CONFIG_SECTION_MAIN = 'main'
    CONFIG_SECTION_SEARCH_PRESET = 'search_preset'
    CONFIG_DEFAULT_CACHE_EXPIRATION = 86400
    CONFIG_DEFAULT_LANGUAGE = 'en-US'

    def __init__(self, settings):
        self.settings = settings

    def parse(self) -> dict:
        """Parse the settings from the plugin."""
        settings = {
            'tmdb_api_key': self.settings.get('tmdb_api_key', section=self.CONFIG_SECTION_MAIN),
            'omdb_api_key': self.settings.get('omdb_api_key', section=self.CONFIG_SECTION_MAIN),
            'cache_expire_after': self.settings.get_int('cache_expire_after', section=self.CONFIG_SECTION_MAIN, fallback=self.CONFIG_DEFAULT_CACHE_EXPIRATION),
            'language': self.settings.get('language', section=self.CONFIG_SECTION_MAIN, fallback=self.CONFIG_DEFAULT_LANGUAGE),
            'search_presets': self._load_search_presets(),
        }

        return settings

    def _load_search_presets(self) -> dict:
        """
        Parse the search presets defined in the settings.
        Each search preset can be customized by the user.
        """
        supported_media_types = ['movie', 'tv']
        settings = self.settings

        search_presets = {}
        for section in settings.sections():
            if section.lower().startswith(self.CONFIG_SECTION_SEARCH_PRESET + '/'):
                enabled = settings.get_bool('enabled', section=section, fallback=True)
                if enabled is False:
                    continue

                section_label = section[len(self.CONFIG_SECTION_SEARCH_PRESET) + 1:].strip()
                label = settings.get_stripped('label', section=section)
                description = settings.get_stripped('description', section=section)
                media_type = settings.get_enum('media_type', section=section, enum=supported_media_types)

                search_args = {}
                search_args_config = settings.get_multiline('search_args', section)
                if search_args_config:
                    for arg in search_args_config:
                        if ' ' not in arg:
                            raise ValueError('malformed {} search_args value from config section [{}]'.format(section))
                        name, value = arg.split(' ', maxsplit=1)
                        search_args[name.strip()] = value.strip()

                try:
                    target = kpu.kwargs_encode(media_type=media_type, search_args=json.dumps(search_args))
                except Exception as exc:
                    continue

                if media_type not in search_presets:
                    search_presets[media_type] = {}

                search_presets[media_type][section_label] = SearchSuggestion(label, description, target)

        return search_presets
