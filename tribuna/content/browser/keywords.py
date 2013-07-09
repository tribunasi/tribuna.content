# -*- coding: utf-8 -*-
"""Keywords widget related code."""

from redomino.advancedkeyword.browser.keywords import KeywordsWidgetGenerator \
    as BaseKeywordsWidgetGenerator
from redomino.advancedkeyword.browser.keywords import KeywordsMapGenerator \
    as BaseKeywordsMapGenerator

from tribuna.content.utils import tags_published


class KeywordsMapGenerator(BaseKeywordsMapGenerator):
    """Keyword tree generator for Keyword Map

       - all the subjects
       - I get subjects from the request (sometimes it doesn't matter)
    """

    def get_all_kw(self):
        return tags_published()


class KeywordsWidgetGenerator(BaseKeywordsWidgetGenerator):
    """Keyword tree generator for Keyword widget

       - all the subjects
       - the subject in the context
    """

    def get_all_kw(self):
        return tags_published()
