from five import grok
from zope import schema

from plone.directives import form

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from tribuna.content import _

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