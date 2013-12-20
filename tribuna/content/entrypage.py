# -*- coding: utf-8 -*-

"""Entry Page content type."""

from datetime import datetime
from five import grok
from plone import api
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.content import _
from tribuna.content.config import ENTRY_PAGES_PATH
from z3c.form import button
from zope import schema
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class SelectOne(Invalid):
    __doc__ = _(u"Only select text or image")


def old_entry_pages():
    """Method for getting all old entry pages for entry page form"""

    catalog = api.portal.get_tool(name='portal_catalog')
    folder = api.content.get(path=ENTRY_PAGES_PATH)
    if not folder:
        return []
    current_id = folder.getDefaultPage()
    brains = catalog(
        portal_type='tribuna.content.entrypage',
        sort_on="Date",
        sort_order="descending"
    )
    old_pages = []

    for item in brains:
        if item.id != current_id:
            title = item.Title or _('No title')
            date = datetime.strptime(
                item.Date.split("+")[0], "%Y-%m-%dT%H:%M:%S").strftime(
                    "%H:%M:%S, %d.%m.%Y")
            old_pages.append(
                (item.id, '{0}, {1}'.format(str(title), str(date))))
    return old_pages


class OldEntryPages(object):
    """Class used for getting vocabulary of entry pages"""

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
        title=_(u"Upload an image"),
        required=False,
    )

    author = schema.TextLine(
        title=_(u"Author"),
        required=False
    )

    font_type = schema.Choice(
        title=_(u"Font type"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('arial', 'arial', u'Arial'),
            SimpleTerm('times', 'times', u'Times New Roman'),
            SimpleTerm('helvetica', 'helvetica', u'Helvetica'),
            SimpleTerm('impact', 'impact', u'Impact'),
            SimpleTerm('cursive', 'cursive', u'Cursive'),
            SimpleTerm('lucida', 'lucida', u'Lucida'),
        ]),
        required=False,
    )

    image_type = schema.Choice(
        title=_(u"Display image"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u'Tiles over page')),
            SimpleTerm('original', 'original', _(u'Original size')),
            SimpleTerm('cover', 'cover', _(u'Cover everything')),
        ]),
        required=False,
    )

    locked_page = schema.Bool(
        title=_(u"Set as default"),
        description=_(u"Set this page as default entry page and disable "
                      "editing."),
        required=False,
    )

def delete_old():
    catalog = api.portal.get_tool(name='portal_catalog')
    brains = catalog(
        portal_type='tribuna.content.entrypage',
        sort_on="Date",
        sort_order="ascending"
    )
    if len(brains) > 20:
        api.content.delete(obj=brains[0].getObject())


class IChangePagePictureForm(form.Schema):
    """Form for adding new picture to entry page"""

    picture = NamedBlobImage(
        title=_(u"Upload an image"),
        required=True,
    )

    image_type = schema.Choice(
        title=_(u"Display image"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u'Tiles over page')),
            # SimpleTerm('original', 'original', _(u'Original size')),
            SimpleTerm('cover', 'cover', _(u'Cover everything')),
        ]),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
        max_length=20
    )

    author = schema.TextLine(
        title=_(u"Author"),
        required=False,
        max_length=20
    )


class ChangePagePictureForm(form.SchemaForm):
    """Form handler for change picture form."""

    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePagePictureForm)

    schema = IChangePagePictureForm
    ignoreContext = True
    label = _(u"Select new page")
    #description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Change'))
    def handleApply(self, action):
        """
        Method that creates new EntryPage and selects it as new default page

        :param    action: Action selected in form
        :type     action: str
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        folder = api.content.get(path=ENTRY_PAGES_PATH)
        new_title = data.get('title') or u'Tribuna'
        with api.env.adopt_roles(['Site Administrator']):
            new_page = api.content.create(
                type='tribuna.content.entrypage',
                title=new_title,
                container=folder)
            api.content.get_state(obj=new_page)
            api.content.transition(obj=new_page, transition='publish')
            new_page.title = new_title
            new_page.picture = data["picture"]
            new_page.author = data.get('author') or u''
            new_page.image_type = data["image_type"]
            folder.setDefaultPage(new_page.id)
            delete_old()
            self.request.response.redirect(api.portal.get().absolute_url())


class IChangePageTextForm(form.Schema):
    """Form for adding text to entry page"""

    text = schema.Text(title=_(u"Text"), max_length=150)
    font_type = schema.Choice(
        title=_(u"Font type"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('arial', 'arial', u'Arial'),
            SimpleTerm('times', 'times', u'Times New Roman'),
            SimpleTerm('helvetica', 'helvetica', u'Helvetica'),
            SimpleTerm('impact', 'impact', u'Impact'),
            SimpleTerm('cursive', 'cursive', u'Cursive'),
            SimpleTerm('lucida', 'lucida', u'Lucida'),
        ]),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Name"),
        required=False,
        max_length=20
    )

    author = schema.TextLine(
        title=_(u"Author"),
        required=False,
        max_length=20
    )

    # @invariant
    # def validateOneSelected(data):
    #     if data.text is None and data.picture is None:
    #         raise SelectOne(_(u"Only select text or image"))
    #     if data.text is not None and data.picture is not None:
    #         raise SelectOne(_(u"Only select text or image"))


class ChangePageTextForm(form.SchemaForm):
    """Form handler for change text on entry page form"""

    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePageTextForm)

    schema = IChangePageTextForm
    ignoreContext = True
    label = _(u"Select new page")

    @button.buttonAndHandler(_(u'Change'))
    def handleApply(self, action):
        """
        Method that creates new EntryPage and selects it as new default page

        :param    action: Action selected in form
        :type     action: str
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        folder = api.content.get(path=ENTRY_PAGES_PATH)
        new_title = data.get('title') or u'Tribuna'
        with api.env.adopt_roles(['Site Administrator']):
            new_page = api.content.create(
                type='tribuna.content.entrypage',
                title=new_title,
                container=folder)
            api.content.get_state(obj=new_page)
            api.content.transition(obj=new_page, transition='publish')
            new_page.title = new_title
            new_page.text = data["text"]
            new_page.author = data.get('author') or u''
            new_page.font_type = data["font_type"]
            folder.setDefaultPage(new_page.id)
            delete_old()
            self.request.response.redirect(api.portal.get().absolute_url())


class IChangePageOldForm(form.Schema):

    old_pages = schema.Choice(
        title=_(u"Select one of the old pages"),
        source=OldEntryPages(),
    )


class ChangePageOldForm(form.SchemaForm):
    """ Defining form handler for change page form."""

    grok.name('change-bar-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(IChangePageOldForm)

    schema = IChangePageOldForm
    ignoreContext = True
    label = _(u"Select entry page")

    @button.buttonAndHandler(_(u'Change'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

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
