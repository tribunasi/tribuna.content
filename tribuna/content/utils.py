#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Various utilites."""

from five import grok
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

# Number of items to display
LIMIT = 15


def get_articles(session):
    """Return a list of all articles depending on the specified filters

    :param session: session object which contains the query parameters
    :returns: a tuple: first item is list of 'intersection' results, while
        second item is a list of 'union' results
    """
    def returnDefaults():
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
    portal_type = ["tribuna.content.article", "Discussion Item", "Image"]
    review_state = "published"
    sort_on = "Date"
    query = None
    operator = "or"
    sort_order = "descending"

    #session.set('content_list', {'union': [], 'intersection': []})

    if 'search-view' in session.keys() and session['search-view']['active']:

        results = catalog(
            SearchableText=session['search-view']['query'], portal_type={
                "query": ["tribuna.content.article", "Discussion Item"],
                "operator": "or"
        })
        return ([content.getObject() for content in results], [])
    if 'portlet_data' not in session.keys():
        return returnDefaults()

    session["default"] = False
    # portal_type
    if session['portlet_data']['content_filters']:
        portal_type = []
        for content_filter in session['portlet_data']['content_filters']:
            if content_filter == 'article':
                portal_type.append("tribuna.content.article")
            elif content_filter == 'comment':
                portal_type.append("Discussion Item")
            elif content_filter == 'image':
                portal_type.append("Image")

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
        return returnDefaults()

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


def count_same(li1, li2):
    return len(set(li1).intersection(set(li2)))


class TagsListHighlighted(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tags_published_highlighted()
        terms = [SimpleVocabulary.createTerm(i[1], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tags_published()
        terms = [SimpleVocabulary.createTerm(i[1], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


def our_unicode(s):
    if not isinstance(s, unicode):
        return unicode(s, 'utf8')
    return s
