from five import grok
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


def tagsPublishedHighlighted():
    catalog = api.portal.get_tool(name='portal_catalog')
    tags = tuple(i.Title for i in catalog(
        portal_type='tribuna.content.tag',
        review_state=['published', 'pending'],
        highlight_in_navigation=True,
    ))
    return tags


def tagsPublished():
    catalog = api.portal.get_tool(name='portal_catalog')
    tags = tuple(i.Title for i in catalog(
        portal_type='tribuna.content.tag',
        review_state=['published', 'pending'],
    ))
    return tags


class TagsListHighlighted(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tagsPublishedHighlighted()
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tagsPublished()
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)
