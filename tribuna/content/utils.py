# -*- coding: utf-8 -*-
"""Various utilites."""

from five import grok
from plone import api
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from tribuna.content import _
from tribuna.content.config import SEARCHABLE_TYPES
from tribuna.content.config import SORT_ON_TYPES

# Number of items to display
LIMIT = 15


def get_articles(form):
    """
    Get articles that match the filters in form.

    :param    form: Selected filters
    :type     form: Dictionary

    :returns: Related articles in intersection (first) and union (second)
    :rtype:   Tuple of two Lists
    """

    query = ""
    try:
        query = form.get("tags").split(',')
    except AttributeError:
        pass

    if not query:
        return get_articles_home(form)

    tags_dict = tags_published_dict()
    query = [tags_dict.get(i) for i in query]

    review_state = "published"
    operator = "or"
    sort_order = "descending"

    filters = form.get("filters")
    portal_type = []
    if filters:
        portal_type = [SEARCHABLE_TYPES.get(i) for i in filters.split(',')
                       if SEARCHABLE_TYPES.get(i)]
    else:
        portal_type = SEARCHABLE_TYPES.values()

    sort_on = SORT_ON_TYPES.get(form.get("sort_on")) or 'Date'

    catalog = api.portal.get_tool(name='portal_catalog')

    all_content = catalog(
        portal_type=portal_type,
        review_state=review_state,
        sort_on=sort_on,
        sort_order=sort_order,
        Subject={'query': query, 'operator': operator},
    )

    all_content = [content for content in all_content]
    all_content.sort(
        key=lambda x: count_same(x.Subject, query), reverse=True)
    all_content = all_content[:LIMIT]

    intersection_count = 0
    num_all_tags = len(query)
    for i in all_content:
        if count_same(i.Subject, query) == num_all_tags:
            intersection_count += 1
        else:
            break

    all_content = [content.getObject() for content in all_content]

    return (all_content[:intersection_count], all_content[intersection_count:])


def get_articles_home(form):
    """
    Get all articles from highlighted tags. Called from home (with no filters)
    and from tags when no tags are selected (with filters).

    :param    form: Selected filters
    :type     form: Dictionary

    :returns: Related articles
    :rtype:   List
    """
    review_state = "published"
    operator = "or"
    sort_order = "descending"

    filters = form.get("filters")
    portal_type = []
    if filters:
        portal_type = [SEARCHABLE_TYPES.get(i) for i in filters.split(',')
                       if SEARCHABLE_TYPES.get(i)]
    else:
        portal_type = SEARCHABLE_TYPES.values()

    sort_on = SORT_ON_TYPES.get(form.get("sort_on")) or 'Date'
    query = [i[1] for i in tags_published_highlighted()]

    catalog = api.portal.get_tool(name='portal_catalog')

    all_content = catalog(
        portal_type=portal_type,
        locked_on_home=True,
        review_state=review_state,
        sort_on=sort_on,
        sort_order=sort_order,
        sort_limit=LIMIT,
        Subject={'query': query, 'operator': operator}
    )[:LIMIT]

    currentLen = len(all_content)

    if currentLen < LIMIT:
        all_content += catalog(
            portal_type=portal_type,
            locked_on_home=False,
            review_state=review_state,
            sort_on=sort_on,
            sort_order=sort_order,
            sort_limit=(LIMIT - currentLen),
            Subject={'query': query, 'operator': operator}
        )[:(LIMIT - currentLen)]

    all_content = [content for content in all_content]
    all_content.sort(
        key=lambda x: count_same(x.Subject, query), reverse=True)
    all_content = all_content[:LIMIT]

    intersection_count = 0
    num_all_tags = len(query)
    for i in all_content:
        if count_same(i.Subject, query) == num_all_tags:
            intersection_count += 1
        else:
            break

    all_content = [content.getObject() for content in all_content]

    return (all_content[:intersection_count], all_content[intersection_count:])


def get_articles_search(form, use_filters=False):

    searchableText = form.get("query")
    # XXX: Do we want to do it like this? Or just search for everything on
    # empty/missing query? It's more or less the same, but not exactly :).
    # This shouldn't happen anymore now, as an empty query goes back to the
    # tags view.
    if not searchableText:
        return get_articles_home(form)

    searchableText = our_unicode(searchableText)
    searchableText = searchableText.strip('"')
    # Save it for the search on Subject
    searchableSubject = searchableText
    searchableText = prepare_search_string(searchableText)

    query = ''
    review_state = "published"
    operator = "or"
    sort_order = "descending"
    portal_type = SEARCHABLE_TYPES.values()
    sort_on = 'Date'

    if use_filters:
        try:
            query = form.get("tags").split(',')
        except AttributeError:
            pass

        if query:
            tags_dict = tags_published_dict()
            query = [tags_dict.get(i) for i in query]
        else:
            query = []

        filters = form.get("filters")
        portal_type = []
        if filters:
            portal_type = [SEARCHABLE_TYPES.get(i) for i in filters.split(',')
                           if SEARCHABLE_TYPES.get(i)]
        else:
            portal_type = SEARCHABLE_TYPES.values()

        sort_on = SORT_ON_TYPES.get(form.get("sort_on")) or 'Date'

    catalog = api.portal.get_tool(name='portal_catalog')

    if query:
        all_content = catalog(
            SearchableText=searchableText,
            portal_type=portal_type,
            review_state=review_state,
            sort_on=sort_on,
            sort_order=sort_order,
            Subject={'query': query, 'operator': operator},
        )
    else:
        all_content = catalog(
            SearchableText=searchableText,
            portal_type=portal_type,
            review_state=review_state,
            sort_on=sort_on,
            sort_order=sort_order,
        )
        # If we're not filtering by Subject, search by Subject too (it's not
        # actually a search, it's just a choice, Plone limitation).
        all_content += catalog(
            Subject=searchableSubject,
            portal_type=portal_type,
            review_state=review_state,
            sort_on=sort_on,
            sort_order=sort_order,
        )

    # XXX: If we want to split into intersection and union, uncomment the
    # bottom two paragraphs

    # all_content = [content for content in all_content]
    # all_content.sort(
    #     key=lambda x: count_same(x.Subject, query), reverse=True)

    all_content = all_content[:LIMIT]

    intersection_count = 0

    # num_all_tags = len(query)
    # for i in all_content:
    #     if count_same(i.Subject, query) == num_all_tags:
    #         intersection_count += 1
    #     else:
    #         break

    # Use a set to get rid of duplicates (duplicates can appear when the query
    # is found both in text and in Subject), then convert back to list so we
    # can work with it.
    all_content = list(set(content.getObject() for content in all_content))

    return (all_content[:intersection_count], all_content[intersection_count:])


def count_same(li1, li2):
    """
    Count how many common elements two lists have.

    :param    li1: First list
    :type     li1: List
    :param    li2: Second list
    :type     li2: List

    :returns: Number of common elements
    :rtype:   Integer
    """
    return len(set(li1).intersection(set(li2)))


def our_unicode(s):
    """
    If not yet unicode, change it to unicode. Made because using the unicode()
    function on a string that is already unicode results in an error.

    :param    s: String to be changed to unicode
    :type     s: String

    :returns: Unicode string
    :rtype:   String
    """
    if not isinstance(s, unicode):
        return unicode(s, 'utf8')
    return s


# XXX
# FIX
def tags_published_highlighted():
    """
    Return IDs and titles of published and pending tags that are marked as
    highlighted.

    :returns: Highlighted tags
    :rtype:   List of Tuples
    """
    with api.env.adopt_user('tags_user'):
        catalog = api.portal.get_tool(name='portal_catalog')
        tags = tuple((i.id, unicode(i.Title, 'utf8')) for i in catalog(
            portal_type='tribuna.content.tag',
            review_state=['published', 'pending'],
            sort_on="getObjPositionInParent",
            highlight_in_navigation=True,
        ))
    return tags


# XXX
# FIX
def tags_published():
    """
    Return IDs and titles of published and pending tags.

    :returns: Tags
    :rtype:   List of Tuples
    """
    with api.env.adopt_user('tags_user'):
        catalog = api.portal.get_tool(name='portal_catalog')
        tags = tuple((i.id, unicode(i.Title, 'utf8')) for i in catalog(
            portal_type='tribuna.content.tag',
            review_state=['published', 'pending'],
            sort_on="sortable_title"
        ))
    return tags


def tags_published_dict(reverse=False):
    """
    Return a dictionary of published tags. Keys are IDs, values are titles, can
    be reversed.

    :param    reverse: Reverse the keys and values
    :type     reverse: Boolean

    :returns: Dictionary with ID-title relations of published tags
    :rtype:   Dictionary
    """
    if reverse:
        return dict((i[1], i[0]) for i in tags_published())
    return dict(tags_published())


def tags_string_to_list(s):
    """
    Convert a string of tag IDs to a list of tag titles.

    :param    s: String of tag IDs
    :type     s: String

    :returns: List of tag titles
    :rtype:   List
    """
    if not s:
        return []
    tags_dict = tags_published_dict()
    return [tags_dict.get(i) for i in s.split(',')]


class TagsListHighlighted(object):
    """Return a vocabulary of highlighted tags"""
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        """
        Get simple vocabulary.

        :param    context: Current context
        :type     context: Context object

        :returns: vocabulary of highlighted tags
        :rtype:   SimpleVocabulary
        """
        items = tags_published_highlighted()
        terms = [SimpleVocabulary.createTerm(i[1], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


class TagsListHighlightedSidebar(object):
    """
    Return a vocabulary of highlighted tags. Here we set the second parameter
    to the ID, because using Titles in GET requests might cause problems.
    """
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        """
        Get simple vocabulary.

        :param    context: Current context
        :type     context: Context object

        :returns: vocabulary of highlighted tags
        :rtype:   SimpleVocabulary
        """
        items = tags_published_highlighted()
        terms = [SimpleVocabulary.createTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


class TagsList(object):
    """Return a vocabulary of all tags"""
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        """
        Get simple vocabulary.

        :param    context: Current context
        :type     context: Context object

        :returns: vocabulary of all tags
        :rtype:   SimpleVocabulary
        """
        items = tags_published()
        terms = [SimpleVocabulary.createTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


class UtilsView(grok.View):
    """View with useful utility methods."""
    grok.context(Interface)
    grok.name('utils')

    def translate(self, string):
        """
        Internally translate a string.

        :param    string: String that we want to translate
        :type     string: String

        :returns: Translated string
        :rtype:   String
        """
        return self.context.translate(_(string))

    def render(self):
        return ''


def quotestring(s):
        return '"%s"' % s


def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        char = our_unicode(char)
        s = s.replace(char, quotestring(char))
    return s


def prepare_search_string(q):
    multispace = u'\u3000'.encode('utf-8')
    for char in ('?', '-', '+', '*', multispace):
        char = our_unicode(char)
        q = q.replace(char, ' ')
    r = q.split()
    r = " AND ".join(r)
    return quote_bad_chars(r) + '*'
