# -*- coding: utf-8 -*-
"""Entry Page content type."""

from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.content import _
from tribuna.content.config import ENTRY_PAGES_PATH
from zope import schema
from z3c.form import button
from plone.dexterity.utils import createContentInContainer
from plone import api
from datetime import datetime
#from plone.formwidget.contenttree import ContentTreeFieldWidget
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
#from zope.schema.vocabulary import SimpleTerm
#from z3c.form import field
#from zope.interface import invariant
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


class SelectOne(Invalid):
    __doc__ = _(u"Only select text or image")


def old_entry_pages():
    catalog = api.portal.get_tool(name='portal_catalog')
    folder = api.content.get(path=ENTRY_PAGES_PATH)
    if not folder:
        return []
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
        items = old_entry_pages()
        terms = [SimpleVocabulary.createTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(terms)


class IEntryPage(form.Schema):
    """Interface for EntryPage content type"""

    title = schema.TextLine(
        title=_(u"Name"),
    )

    text = schema.TextLine(
        title=_(u"Text"),
        required=False
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )

    author = schema.TextLine(
        title=_(u"Author"),
        required=False
    )

    font_type = schema.Choice(
        title=_(u"Type of sorting"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('arial', 'arial', _(u'arial')),
            SimpleTerm('times', 'times', _(u'times_new_roman')),
            SimpleTerm('latest', 'latest', _(u'Latest')),
        ]),
        required=False,
    )

    image_type = schema.Choice(
        title=_(u"image type"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u'Tiles over page')),
            SimpleTerm('original', 'original', _(u'Original size')),
            SimpleTerm('cover', 'cover', _(u'Cover everything')),
        ]),
        required=False,
    )
    locked_page = schema.Bool(
        title=_(u"Is entry page locked on this?"),
        required=False,
    )


class IChangePagePictureForm(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    author = schema.TextLine(
        title=_(u"Author"),
        required=False
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )

    image_type = schema.Choice(
        title=_(u"image type"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u'Tiles over page')),
            SimpleTerm('original', 'original', _(u'Original size')),
            SimpleTerm('cover', 'cover', _(u'Cover everything')),
        ]),
        required=True,
    )
    # @invariant
    # def validateOneSelected(data):
    #     if data.text is None and data.picture is None:
    #         raise SelectOne(_(u"Only select text or image"))
    #     if data.text is not None and data.picture is not None:
    #         raise SelectOne(_(u"Only select text or image"))


class ChangePagePictureForm(form.SchemaForm):
    """Defining form handler for change page form."""

    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePagePictureForm)

    schema = IChangePagePictureForm
    ignoreContext = True
    label = _(u"Select new page")
    #description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Change Picture'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        folder = api.content.get(path=ENTRY_PAGES_PATH)
        new_title = data["title"]
        new_title = str(data["title"]) + " - " + str(unicode(datetime.now()))
        with api.env.adopt_user(username="admin1"):
            new_page = api.content.create(
                type='tribuna.content.entrypage',
                title=new_title,
                container=folder)
            api.content.get_state(obj=new_page)
            api.content.transition(obj=new_page, transition='publish')
            new_page.title = new_title
            new_page.picture = data["picture"]
            new_page.author = data["author"]
            new_page.image_type = data["image_type"]
            folder.setDefaultPage(new_page.id)
            self.request.response.redirect(api.portal.get().absolute_url())


class IChangePageTextForm(form.Schema):

    title = schema.TextLine(
        title=_(u"Name"),
        required=False
    )

    author = schema.TextLine(
        title=_(u"Author"),
        required=False
    )

    text = schema.TextLine(
        title=_(u"Text"),
        required=False
    )

    font_type = schema.Choice(
        title=_(u"font type"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('arial', 'arial', _(u'Arial')),
            SimpleTerm('times', 'times', _(u'Times New Roman')),
            SimpleTerm('helvetica', 'helvetica', _(u'Helvetica')),
        ]),
        required=True,
    )

    # @invariant
    # def validateOneSelected(data):
    #     if data.text is None and data.picture is None:
    #         raise SelectOne(_(u"Only select text or image"))
    #     if data.text is not None and data.picture is not None:
    #         raise SelectOne(_(u"Only select text or image"))


class ChangePageTextForm(form.SchemaForm):
    """ Defining form handler for change page form"""

    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePageTextForm)

    schema = IChangePageTextForm
    ignoreContext = True
    label = _(u"Select new page")
    #description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Change Text'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        folder = api.content.get(path=ENTRY_PAGES_PATH)
        new_title = data["title"]
        new_title = str(data["title"]) + " - " + str(unicode(datetime.now()))
        with api.env.adopt_user(username="admin1"):
            new_page = api.content.create(
                type='tribuna.content.entrypage',
                title=new_title,
                container=folder)
            api.content.get_state(obj=new_page)
            api.content.transition(obj=new_page, transition='publish')
            new_page.title = new_title
            new_page.text = data["text"]
            new_page.author = data["author"]
            new_page.font_type = data["font_type"]
            folder.setDefaultPage(new_page.id)
            self.request.response.redirect(api.portal.get().absolute_url())


class IChangePageOldForm(form.Schema):

    old_pages = schema.Choice(title=u"Select one of the old pages",
                              source=OldEntryPages(),
                              )
    # @invariant
    # def validateOneSelected(data):
    #     if data.text is None and data.picture is None:
    #         raise SelectOne(_(u"Only select text or image"))
    #     if data.text is not None and data.picture is not None:
    #         raise SelectOne(_(u"Only select text or image"))


class ChangePageOldForm(form.SchemaForm):
    """ Defining form handler for change page form."""

    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePageOldForm)

    schema = IChangePageOldForm
    ignoreContext = True
    label = _(u"Select new page")
    #description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Change old'))
    def handleApply(self, action):
        data, errors = self.extractData()
        #if errors:
        #    self.status = self.formErrorsMessage
        #    return

        folder = api.content.get(path=ENTRY_PAGES_PATH)
        page_id = data["old_pages"]
        folder.setDefaultPage(page_id)
        self.request.response.redirect(api.portal.get().absolute_url())


class View(grok.View):
    """Entry page view"""

    grok.context(IEntryPage)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)

    def change_page_picture(self):
        """Return a form which can change the entry page."""
        form1 = ChangePagePictureForm(self.context, self.request)
        form1.update()
        return form1

    def change_page_text(self):
        """Return a form which can change the entry page."""
        form1 = ChangePageTextForm(self.context, self.request)
        form1.update()
        return form1

    def change_page_old(self):
        """Return a form which can change the entry page."""
        form1 = ChangePageOldForm(self.context, self.request)
        form1.update()
        return form1
