
from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.content import _
from zope import schema
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from plone import api
from datetime import datetime
from plone.formwidget.contenttree import ContentTreeFieldWidget
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from z3c.form import field
from zope.interface import invariant, Invalid

class SelectOne(Invalid):
    __doc__ = _(u"Only select text or image")


def old_entry_pages():
    catalog = api.portal.get_tool(name='portal_catalog')
    folder = catalog(id="entry-pages")[0].getObject()
    current_id = folder.getDefaultPage()
    old_pages = tuple((i.id, i.Title) for i in catalog(
        portal_type='tribuna.content.entrypage',
    ) if i.id != current_id)
    return old_pages


class OldEntryPages(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        #import pdb; pdb.set_trace()
        items = old_entry_pages()
        terms = [SimpleVocabulary.createTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


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

    title = schema.TextLine(
        title=_(u"Name"),
        required=False
    )

    text = schema.TextLine(
        title=_(u"Text"),
        required=False
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )

    #form.widget(old_pages=ContentTreeFieldWidget)
    old_pages = schema.Choice(title=u"Select one of the old pages",
                              source=OldEntryPages(),
                              )

    @invariant
    def validateOneSelected(data):
        if data.text is None and data.picture is None:
            raise SelectOne(_(u"Only select text or image"))
        if data.text is not None and data.picture is not None:
            raise SelectOne(_(u"Only select text or image"))


class ChangePageForm(form.SchemaForm):
    """ Defining form handler for change page form

    """
    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePageForm)

    schema = IChangePageForm
    ignoreContext = True
    label = _(u"Select new page")
    description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Change'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            #import pdb; pdb.set_trace()
            self.status = self.formErrorsMessage
            return
        catalog = api.portal.get_tool(name='portal_catalog')
        folder = catalog(id="entry-pages")[0].getObject()
        new_title = data["title"]
        if not new_title or new_title == "":
            new_title = unicode(datetime.now())
        new_page = createContentInContainer(folder, "tribuna.content.entrypage", title=new_title)
        api.content.get_state(obj=new_page)
        api.content.transition(obj=new_page, transition='publish')
        new_page.text = data["text"]
        new_page.picture = data["picture"]
        #import pdb; pdb.set_trace()
        folder.setDefaultPage(new_page.id)
        self.request.response.redirect(api.portal.get().absolute_url())

    @button.buttonAndHandler(_(u'Change to old page'))
    def handleApply(self, action):
        data, errors = self.extractData()
        #if errors:
        #    self.status = self.formErrorsMessage
        #    return

        catalog = api.portal.get_tool(name='portal_catalog')
        folder = catalog(id="entry-pages")[0].getObject()
        #import pdb; pdb.set_trace()
        page_id = data["old_pages"]
        folder.setDefaultPage(page_id)
        self.request.response.redirect(api.portal.get().absolute_url())


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
