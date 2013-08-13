# -*- coding: utf-8 -*-
"""Global configuration and constants."""

# Path to the folder that holds the entry pages
ENTRY_PAGES_PATH = '/entry-pages'

# Content types that should show up in search results
# keys are 'friendly' ids, used in forms etc., values are actual Plone
# content type ids
SEARCHABLE_TYPES = {
    'article': 'tribuna.content.article',
    'comment': 'Discussion Item',
    'image': 'tribuna.content.image'
}
