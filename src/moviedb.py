import os
import sys

import keypirinha as kp
import keypirinha_util as kpu

from MovieDB import constants
from .settingsparser import SettingsParser
from .suggestions.errorsuggestion import ErrorSuggestion
from .suggestions.textsuggestion import TextSuggestion
from .userinputparser import UserInputParser
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from .suggester import Suggester
import requests_cache

class Moviedb(kp.Plugin):

    def __init__(self):
        super().__init__()
        self.icons = {}
        self.current_page = 1
        self.current_suggestions = None
        self.user_input = None
        self.input_parser = UserInputParser()

    def on_start(self):
        self._load_icons()
        self._read_config()

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='MovieDB: Search movies',
                short_desc='Search for movies in the TMDB database',
                target='movie',
                icon_handle=self.icons['Movies'],
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            ),
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='MovieDB: Search TV shows',
                short_desc='Search for TV shows in the TMDB database',
                target='tv',
                icon_handle=self.icons['TV'],
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            ),
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='MovieDB: Search people',
                short_desc='Search for people in the TMDB database',
                target='people',
                icon_handle=self.icons['Person'],
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            )
        ])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD:
            return

        suggestions = []
        selected_chain = items_chain[len(items_chain) - 1]
        match_type = kp.Match.ANY

        if not user_input:
            results, match_type = self.suggester.without_input(selected_chain)
        else:
            results, match_type = self.suggester.with_input(selected_chain, user_input)

        if isinstance(results, list):
            if not results and user_input:
                results = [ErrorSuggestion('No results', 'No results found')]

            suggestions = self._create_suggestions_items(results)
            self.set_suggestions(suggestions, match_type, kp.Sort.NONE)

    def on_execute(self, item, action):
        """Perform an action related with the selected item/action item."""
        item_category = item.category()
        item_label = item.label()

        try:
            item_target = kpu.kwargs_decode(item.target())
        except Exception:
            item_target = item.target()

        # Open in browser if there it is an URL in the target
        if 'url' in item_target:
            url = item_target['url']
            # If it is a moviedb url to be opened, append the language query
            if constants.URL_MOVIEDB_BASE in url:
                url += '?language={}'.format(self.settings['language'])

            kpu.web_browser_command(url=url, execute=True)

        # Copy text
        if item_category == TextSuggestion.ITEM_CAT:
            kpu.set_clipboard(item_label)

    def on_events(self, flags):
        """Performs an action when some events occurs."""
        if flags & kp.Events.PACKCONFIG:
            self._read_config()

    def _create_suggestions_items(self, results):
        suggestions = []
        for item in results:
            try:
                if isinstance(item, ErrorSuggestion):
                    suggestions.append(self.create_error_item(label=item.label, short_desc=item.description))
                else:
                    suggestions.append(self.create_item(
                        category=item.category,
                        label=item.label,
                        short_desc=item.description,
                        target=item.target,
                        data_bag=item.data_bag,
                        icon_handle=self.icons[item.icon] if item.icon else None,
                        args_hint=kp.ItemArgsHint.FORBIDDEN,
                        hit_hint=kp.ItemHitHint.IGNORE,
                        loop_on_suggest=item.loop_on_suggest
                    ))
            except Exception as exc:
                self.err(exc)
                continue

        return suggestions

    def _read_config(self):
        """Parses the settings when it has been updated by the user."""
        self.settings = SettingsParser(self.load_settings()).parse()
        self._configure_cache()
        self.suggester = Suggester(self.settings, self.icons)

    def _configure_cache(self):
        """Configures the cache (when the items expire)."""
        requests_cache.install_cache(os.path.join(self.get_package_cache_path(True), 'requests'), backend='filesystem', expire_after=self.settings['cache_expire_after'])

    def _load_icons(self):
        """Loads the icons used in this plugin."""
        for icon in self.icons.values():
            icon.free()

        path = 'res://{}'.format(self.package_full_name())
        resources = self.find_resources('*.png')

        for resource in resources:
            icon = self.load_icon('{}/{}'.format(path, resource))
            icon_name = resource.split('/')[1].replace('.png', '')
            self.icons[icon_name] = icon
