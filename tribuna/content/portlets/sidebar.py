from five import grok
from plone import api
from plone.directives import form
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements

from tribuna.content import _
from tribuna.content.mainpage import MainPageView

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.interfaces import ISiteRoot
from z3c.form import button

import urllib2
import urllib


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



class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    tags = schema.List(
            title=u"Tags",
            # source=CountriesList(),
            value_type=schema.Choice(source=TagsList()),
            default=[]
        )


@form.default_value(field=ISidebarForm['tags'])
def default_title(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if("tags" in session.keys()):
        return session["tags"]["tags"]
    else:
        return []


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

    @button.buttonAndHandler(u'Send-Union')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set("tags", data)
        session.set("is_union", True)
        self.request.response.redirect("http://localhost:8080/Plone/@@main-page")

    @button.buttonAndHandler(u'Send-Intersection')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set("tags", data)
        session.set("is_union", False)
        self.request.response.redirect("http://localhost:8080/Plone/@@main-page")

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


class ISidebarPortlet(IPortletDataProvider):
    pass


class Assignment(base.Assignment):
    implements(ISidebarPortlet)

    heading = _(u"Sidebar navigation")
    description = _(u"Use this portlet for sidebag tag navigation.")

    title = _(u"Sidebar portlet")

    def tags(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        return catalog(portal_type="tribuna.content.tag")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('sidebar.pt')

    def tags(self):
        """Return a catalog search result of articles that have this tag
        """

        form1 = SidebarForm(self.context, self.request)
        form1.update()
        return form1
        # catalog = api.portal.get_tool(name='portal_catalog')
        # return catalog(portal_type="tribuna.content.tag")

    def callMainPage(self, tag):
        return "localhost:8080/Plone/" + tag


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()


