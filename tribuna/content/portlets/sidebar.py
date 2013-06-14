from five import grok
from plone import api
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


from tribuna.content import _
from tribuna.content.utils import tagsPublished


# SimpleTerm(value (actual value), token (request), title (shown in browser))

class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        items = tagsPublished()
        terms = [SimpleVocabulary.createTerm(i, i, i) for i in items]
        return SimpleVocabulary(terms)


class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    form.widget(tags=CheckBoxFieldWidget)
    tags = schema.List(
        title=_(u"Tags"),
        value_type=schema.Choice(source=TagsList()),
    )

    sort_choice = schema.Choice(
        title=_(u"Type of sorting articles"),
        vocabulary=SimpleVocabulary([
            SimpleTerm(u'comments', u'comments', _(u'Nr. of comments')),
            SimpleTerm(u'latest', u'latest', _(u'Latest')),
        ]),
    )

    form.widget(content_filters=CheckBoxFieldWidget)
    content_filters = schema.List(
        title=_(u"Content filters"),
        value_type=schema.Choice(source=SimpleVocabulary([
            SimpleTerm(u'articles', u'articles', _(u'Articles')),
            SimpleTerm(u'comments', u'comments', _(u'Comments')),
            SimpleTerm(u'images', u'images', _(u'Images')),
        ])),
    )

    sort_type = schema.Choice(
        title=_(u"How to apply tags"),
        vocabulary=SimpleVocabulary([
            SimpleTerm(u'union', u'union', _(u'Union')),
            SimpleTerm(u'intersection', u'intersection', _(u'Intersection')),
        ]),
    )


@form.default_value(field=ISidebarForm['tags'])
def default_tags(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if(u"portlet_data" in session.keys()):
        return session[u"portlet_data"][u"tags"]
    else:
        return []


@form.default_value(field=ISidebarForm['sort_choice'])
def default_sort_choice(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if(u"portlet_data" in session.keys()):
        if(u"sort_choice" in session["portlet_data"].keys()):
            return session[u"portlet_data"][u"sort_choice"]
    else:
        return u"latest"


@form.default_value(field=ISidebarForm['content_filters'])
def default_content_filters(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if(u"portlet_data" in session.keys()):
        return session[u"portlet_data"][u"content_filters"]
    else:
        return []


@form.default_value(field=ISidebarForm['sort_type'])
def default_sort_type(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if(u"portlet_data" in session.keys()):
        if(u"sort_choice" in session["portlet_data"].keys()):
            return session[u"portlet_data"][u"sort_type"]
    else:
        return u"union"


class SidebarForm(form.SchemaForm):
    """ Defining form handler for sidebar portlet

    """
    grok.name('my-form')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = ISidebarForm
    ignoreContext = True

    label = u"Select appropriate tags"
    description = u"Tags selection form"

    @button.buttonAndHandler(u'Filter')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set("portlet_data", data)
        #session.set("is_union", is_union)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/@@main-page".format(url))

    # @button.buttonAndHandler(u'Send-Union')
    # def handleApply(self, action):
    #     self._handleApply(action, True)

    # @button.buttonAndHandler(u'Send-Intersection')
    # def handleApply(self, action):
    #     self._handleApply(action, False)

    # @button.buttonAndHandler(u"Cancel")
    # def handleCancel(self, action):
    #     """User cancelled. Redirect back to the front page.
    #     """


class ISidebarPortlet(IPortletDataProvider):
    pass


class Assignment(base.Assignment):
    implements(ISidebarPortlet)

    heading = _(u"Sidebar navigation")
    description = _(u"Use this portlet for sidebag tag navigation.")

    title = _(u"Sidebar portlet")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('sidebar.pt')

    def portlet_data(self):
        """Return a catalog search result of articles that have this tag
        """
        form1 = SidebarForm(self.context, self.request)
        form1.update()
        return form1


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
