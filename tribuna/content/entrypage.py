
from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.content import _
from zope import schema
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from plone import api
from datetime import datetime


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


class IChangePageForm(form.Schema):
    text = schema.TextLine(
        title=_(u"Text"),
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )


class ChangePageForm(form.SchemaForm):
    """ Defining form handler for change page form

    """
    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.context(IChangePageForm)

    schema = IChangePageForm
    ignoreContext = True

    label = _(u"Select new page")
    description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Change'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        catalog = api.portal.get_tool(name='portal_catalog')
        folder = catalog(id="entry-pages")[0].getObject()
        new_page = createContentInContainer(folder, "tribuna.content.entrypage", title=unicode(datetime.now()))
        new_page.text = data["text"]
        import pdb; pdb.set_trace()
        self.request.response.redirect(new_page.absolute_url())


class View(grok.View):
    grok.context(IEntryPage)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)

    def change_page(self):
        """Return a form which can change the entry page
        """
        form1 = ChangePageForm(self.context, self.request)
        form1.update()
        return form1
