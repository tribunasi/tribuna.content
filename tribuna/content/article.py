from five import grok
from plone import api
from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage
from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from tribuna.content import _


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog({
            'portal_type': 'tribuna.content.tag',
            'review_state': 'published',
        })

        terms = []

        for item in items:
            term = item.Title
            terms.append(SimpleVocabulary.createTerm(term, term, term))

        return SimpleVocabulary(terms)


class IArticle(form.Schema):
    """Interface for Article content type
    """

    title = schema.TextLine(
        title=_(u"Name"),
    )

    description = schema.Text(
        title=_(u"Article text"),
    )

    picture = NamedImage(
        title=_(u"Article image"),
        description=_(u"Upload an image for your article"),
        required=False,
    )

    tags = schema.List(
        title=u"Tags",
        # source=CountriesList(),
        value_type=schema.Choice(source=TagsList()),
    )
