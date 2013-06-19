
from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.content import _
from zope import schema


class IEntryPage(form.Schema):
    """Interface for EntryPage content type
    """

    title = schema.TextLine(
        title=_(u"Name"),
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )


class ChangePageForm(form.schema):
    title = schema.TextLine(
        title=_(u"Name"),
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )

class View(grok.View):
    grok.context(IEntryPage)
    grok.require('zope2.View')

    def change_page(self):
        """Return a form which can change the entry page
        """
        form1 = ChangePageForm(self.context, self.request)
        form1.update()
        return form1
