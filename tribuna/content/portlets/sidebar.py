from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from tribuna.content import _


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
        catalog = api.portal.get_tool(name='portal_catalog')
        return catalog(portal_type="tribuna.content.tag")


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
