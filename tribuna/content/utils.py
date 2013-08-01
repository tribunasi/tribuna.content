#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Various utilites."""

from five import grok
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

# XXX
# FIX
def tags_published_highlighted():
    with api.env.adopt_user('tags_user'):
        catalog = api.portal.get_tool(name='portal_catalog')
        tags = tuple((i.id, unicode(i.Title, 'utf8')) for i in catalog(
            portal_type='tribuna.content.tag',
            review_state=['published', 'pending'],
            sort_on="sortable_title",
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
