from five import grok
from zope import schema

from plone.directives import form

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from tribuna.content import _

class ITag(form.Schema):
    """Interface for Tag content type
    """

    title = schema.TextLine(
            title=_(u"Name"),
        )

    description = schema.Text(
            title=_(u"A short summary"),
        )

    picture = NamedImage(
            title=_(u"Picture"),
            description=_(u"Please upload an image"),
            required=False,
        )