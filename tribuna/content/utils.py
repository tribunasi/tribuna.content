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
    Gets all the articles that matches the selected filters in session

    :param    session: Current session
    :type     session: Session object

    :returns: first item is list of 'intersection' results, while
        second item is a list of 'union' results
    :rtype:   tuple
    """
    def return_defaults():
        """
        Method for returning articles that get selected when no filters are
        present

        :returns: first item is list of 'intersection' results, while
            second item is a list of 'union' results
        :rtype:   tuple
        """
        pass
        # query = [i[1] for i in tags_published_highlighted()]
        # all_content = catalog(
        #     portal_type=portal_type,
        #     locked_on_home=True,
        #     review_state=review_state,
        #     sort_on=sort_on,
        #     sort_order=sort_order,
        #     sort_limit=LIMIT,
        #     Subject={'query': query, 'operator': operator}
        # )[:LIMIT]

        # currentLen = len(all_content)

        # if currentLen < LIMIT:
        #     all_content += catalog(
        #         portal_type=portal_type,
        #         locked_on_home=False,
        #         review_state=review_state,
        #         sort_on=sort_on,
        #         sort_order=sort_order,
        #         sort_limit=(LIMIT - currentLen),
        #         Subject={'query': query, 'operator': operator}
        #     )[:(LIMIT - currentLen)]

        # all_content = [content for content in all_content]
        # all_content.sort(
        #     key=lambda x: count_same(x.Subject, query), reverse=True)
        # all_content = all_content[:LIMIT]

        # intersection_count = 0
        # num_all_tags = len(query)
        # for i in all_content:
        #     if count_same(i.Subject, query) == num_all_tags:
        #         intersection_count += 1
        #     else:
        #         break

        # all_content = [content.getObject() for content in all_content]
        # session["search-view"] = {}
        # session["search-view"]['active'] = False
        # session["default"] = True
        # return (
        #     all_content[:intersection_count],
        #     all_content[intersection_count:]
        # )

    catalog = api.portal.get_tool(name='portal_catalog')

    review_state = "published"
    operator = "or"
    sort_order = "descending"

    query = ""
    try:
        query = form.get("tags").split(',')
    except AttributeError:
        pass

    tags_dict = tags_published_dict()

    query = [tags_dict.get(i) for i in query]

    sort_on = SORT_ON_TYPES.get(form.get("sort_on")) or 'Date'

    filters = form.get("filters", "article,comment,image")
    portal_type = [SEARCHABLE_TYPES.get(i) for i in filters.split(',')
                   if SEARCHABLE_TYPES.get(i)]

    if not query:
        return return_defaults()

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


def get_articles_old(session):
    """
    Gets all the articles that matches the selected filters in session

    :param    session: Current session
    :type     session: Session object

    :returns: first item is list of 'intersection' results, while
        second item is a list of 'union' results
    :rtype:   tuple
    """
    def return_defaults():
        """
        Method for returning articles that get selected when no filters are
        present

        :returns: first item is list of 'intersection' results, while
            second item is a list of 'union' results
        :rtype:   tuple
        """
        query = [i[1] for i in tags_published_highlighted()]
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
        session["search-view"] = {}
        session["search-view"]['active'] = False
        session["default"] = True
        return (
            all_content[:intersection_count],
            all_content[intersection_count:]
        )

    catalog = api.portal.get_tool(name='portal_catalog')

    portal_type = []

    review_state = "published"
    sort_on = "Date"
    query = None
    operator = "or"
    sort_order = "descending"

    if 'search-view' in session.keys() and session['search-view']['active']:
        results = catalog(

            SearchableText=session['search-view']['query'],
            portal_type={
                "query": [
                    "tribuna.content.article",
                    "Discussion Item",
                    "tribuna.content.image"
                    ],
                "operator": "or"
                },
            review_state="published",
            )
        return ([content.getObject() for content in results], [])
    if 'portlet_data' not in session.keys():
        return return_defaults()

    session["default"] = False

    # portal_type
    if session['portlet_data']['content_filters']:
        portal_type = []
        for content_filter in session['portlet_data']['content_filters']:
            portal_type.append(SEARCHABLE_TYPES.get(content_filter))

    # sort_on
    tmp = session['portlet_data']['sort_on']
    if tmp == 'latest':
        sort_on = 'Date'
        sort_order = 'descending'
    elif tmp == 'alphabetical':
        sort_on = 'sortable_title'
        sort_order = 'descending'
    elif tmp == 'comments':
        sort_on = 'total_comments'
        sort_order = 'descending'

    if(session['portlet_data']['tags'] == [] and
       session['portlet_data']['all_tags'] == []):
        return return_defaults()

    all_content = []
    session['portlet_data']['tags'] = \
        list(set(session['portlet_data']['tags'] +
                 session['portlet_data']['all_tags']))

    query = session['portlet_data']['tags']

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
    session["search-view"]['active'] = False

    return (all_content[:intersection_count], all_content[intersection_count:])


def count_same(li1, li2):
    return len(set(li1).intersection(set(li2)))


def our_unicode(s):
    if not isinstance(s, unicode):
        return unicode(s, 'utf8')
    return s


# XXX
# FIX
def tags_published_highlighted():
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
    with api.env.adopt_user('tags_user'):
        catalog = api.portal.get_tool(name='portal_catalog')
        tags = tuple((i.id, unicode(i.Title, 'utf8')) for i in catalog(
            portal_type='tribuna.content.tag',
            review_state=['published', 'pending'],
            sort_on="sortable_title"
        ))
    return tags


def tags_published_dict():
    return dict(tags_published())


def set_default_view_type(session):
    """
    Set the default view_type to drag

    :param    session: current session
    :type     session: Session object
    """
    session.set('view_type', 'drag')

def set_default_filters(session):
    """
    Set default filters - no tags, sort on latest and all filters enabled

    :param    session: current session
    :type     session: Session object
    """

    session.set('portlet_data', {
        'all_tags': [],
        'tags': [],
        'sort_on': 'latest',
        'content_filters': ['article', 'comment', 'image']
    })

def reset_session(session, default):
    """
    Fill the session with default data if it's empty of specifically asks
    for it

    :param    session: Current session
    :type     session: Session object
    :param    default: True or False depending on if we selected default view
    :type     default: boolean
    """
    if default:
        for key in session.keys():
            del session[key]
    if default or 'portlet_data' not in session.keys():
        set_default_filters(session)
    if default or 'view_type' not in session.keys():
        set_default_view_type(session)


class TagsListHighlighted(object):
    """Return a vocabulary of highlighted tags"""
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        """
        Get simple vocabulary

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
        Get simple vocabulary

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
        Method for internaly translating string

        :param    string: String that we want to translate
        :type     string: str

        :returns: translated string
        :rtype:   str
        """
        return self.context.translate(_(string))

    def get_selected_tags(self):
        """
        Get a list of selected tags from the session.

        :returns: Selected tags
        :rtype:   list
        """
        session = self.context.session_data_manager.getSessionData(create=True)
        data = session.get('portlet_data', None)
        return data and data.get('tags', []) or []

    def render(self):
        return ''
