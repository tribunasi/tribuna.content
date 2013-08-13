#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Viewlets."""

from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget
from five import grok
from plone import api
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import common as base
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

from tribuna.content.homepage import HomePageView
from tribuna.content.mainpage import MainPageView
from tribuna.content.utils import get_articles

# set the directory for templates
grok.templatedir('templates')


def get_viewlet(context=None, request=None, manager=None, name=None):
    """Helper method for getting the viewlet for the provided viewlet name
    and viewlet manager.

    :param context: context object
    :param request: request
    :param manager: viewlet manager, for which the viewlet is registered
    :param name: viewlet name
    :returns: viewlet, if found, None otherwise
    """

    # viewlet managers also require a view object for adaptation
    view = BrowserView(context, request)
    if not IViewView.providedBy(view):
        alsoProvides(view, IViewView)

    # viewlet managers are found by Multi-Adapter lookup
    manager = getMultiAdapter(
        (context, request, view), IViewletManager, manager)

    # calling update() on a manager causes it to set up its viewlets
    manager.update()

    all_viewlets = manager.viewlets
    for viewlet in all_viewlets:
        if viewlet.__name__ == name:
            return viewlet


class NavbarViewlet(base.ViewletBase):
    """Our custom global navigation viewlet."""
    implements(IViewlet)

    def default_page_url(self):
        portal = api.portal.get()
        entry_pages = portal["entry-pages"]
        default_page = entry_pages[entry_pages.getDefaultPage()]

        return default_page.absolute_url()


class DefaultSessionViewlet(BrowserView):
    """Viewlet for managing the session"""

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(DefaultSessionViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def set_default_content_list(self, session):
        get_articles(session)

    def set_default_view_type(self, session):
        session.set('view_type', 'drag')

    def reset_session(self):
        """Check if we have the data, if we don't, initialize session
        parameters.
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        get_default = self.request.get('default')
        if get_default and "portlet_data" in session.keys():
            del session["portlet_data"]
        if get_default or 'content_list' not in session.keys():
            self.set_default_content_list(session)
        if get_default or 'view_type' not in session.keys():
            self.set_default_view_type(session)

    def render(self):
        if (isinstance(self.__parent__, HomePageView)
                or isinstance(self.__parent__, MainPageView)):
            self.reset_session()
        return ""


class CommentsView(grok.View):
    """View for rendering the comments viewlet.

    XXX: We need this e.g. on the @@articles view, because we load the
    content via AJAX and we don't have a proper article context.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('comments-view')

    def render_comments(self):
        """Render the comments viewlet."""
        viewlet = get_viewlet(
            context=self.context,
            request=self.request,
            manager=u'plone.belowcontent',
            name=u'plone.comments'
        )
        # Set the widget factory for our field
        viewlet.form.fields['subject'].widgetFactory['input'] =\
            TokenInputFieldWidget

        # Update widgets so it takes effect
        viewlet.form.updateWidgets()
        return viewlet.render()


class ContentActionsView(grok.View):
    """View for rendering the content actions.

    XXX: We need this e.g. on the @@articles view, because we load the
    content via AJAX and we don't have a proper article context.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('contentactions-view')

    def render_content_actions(self):
        """Render content actions viewlet (dropdown with 'Copy', 'Cut',
        changing the workflow state etc.).
        """
        viewlet = get_viewlet(
            context=self.context,
            request=self.request,
            manager=u'plone.contentviews',
            name=u'plone.contentactions'
        )
        return viewlet.render()
