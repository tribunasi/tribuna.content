from five import grok
from plone.api.portal import get_tool
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


def tagsPublished():
    catalog = get_tool(name='portal_catalog')
    tags = tuple(i.Title for i in catalog(
        portal_type='tribuna.content.tag',
        review_state='published',
    ))
    return tags


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tagsPublished()
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)
