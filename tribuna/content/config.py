"""Global configuration and constants."""

# Path to the folder that holds the entry pages
ENTRY_PAGES_PATH = '/entry-pages'

# Content types that should show up in search results
# keys are 'friendly' ids, used in forms etc., values are actual Plone
# content type ids
SEARCHABLE_TYPES = {
    'article': 'tribuna.content.article',
    'comment': 'Discussion Item',
    'image': 'tribuna.content.image',
    'annotation': 'tribuna.annotator.annotation'
}

SORT_ON_TYPES = {
    'latest': 'Date',
    'comments': 'total_comments',
}

TYPE_TO_VIEW = {
    'Discussion Item': 'comment-view',
    'tribuna.content.image': 'image-view',
    'tribuna.content.article': 'view',
    'tribuna.annotator.annotation': 'view',
}
