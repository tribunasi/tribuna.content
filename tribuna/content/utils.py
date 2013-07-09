# -*- coding: utf-8 -*-
"""Various utilites."""

from five import grok
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


def tags_published_highlighted():
    catalog = api.portal.get_tool(name='portal_catalog')
    tags = tuple(i.Title for i in catalog(
        portal_type='tribuna.content.tag',
        review_state=['published', 'pending'],
        highlight_in_navigation=True,
    ))
    return tags


def tags_published():
    catalog = api.portal.get_tool(name='portal_catalog')
    tags = tuple(i.Title for i in catalog(
        portal_type='tribuna.content.tag',
        review_state=['published', 'pending'],
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
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tags_published()
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)
