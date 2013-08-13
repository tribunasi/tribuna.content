#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Article content type."""

from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget
from five import grok
from plone import api
from plone.app.layout.globals.interfaces import IViewView
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from Products.Five.browser import BrowserView
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

from tribuna.content import _


class IArticle(form.Schema):
    """Interface for Article content type."""

    title = schema.TextLine(
        title=_(u"Name"),
    )

    description = schema.Text(
        title=_(u"Article description"),
    )

    picture = NamedBlobImage(
        title=_(u"Image"),
        description=_(u"Will be displayed on the article view."),
        required=False,
    )


class CommentsView(grok.View):
    """View for showing all the comments on the article and adding new
    comments.
    """

    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('comments-view')

    def get_comment_viewlet(self):
        """Method for getting comments viewlet so we can use it in
        other views"""

        request = self.request
        context = self.context

        # viewlet managers also require a view object for adaptation
        view = BrowserView(context, request)
        if not IViewView.providedBy(view):
            alsoProvides(view, IViewView)

        # finally, you need the name of the manager you want to find
        manager_name = 'plone.belowcontent'

        # viewlet managers are found by Multi-Adapter lookup
        manager = getMultiAdapter(
            (context, request, view), IViewletManager, manager_name)

        # calling update() on a manager causes it to set up its viewlets
        manager.update()

        all_viewlets = manager.viewlets
        for viewlet in all_viewlets:
            if viewlet.__name__ == u"plone.comments":
                # Set the widget factory for our field
                viewlet.form.fields['subject'].widgetFactory['input'] =\
                    TokenInputFieldWidget
                # Update widgets so it takes effect
                viewlet.form.updateWidgets()
                return viewlet.render()


class ContentActionsView(grok.View):
    """View for showing the content actions. Looks like Plone really needs
    his context to work properly.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('contentactions-view')

    def get_contentactions_viewlet(self):
        """Method for getting content actions viewlet so we can use it in
        other views"""

        request = self.request
        context = self.context

        # viewlet managers also require a view object for adaptation
        view = BrowserView(context, request)
        if not IViewView.providedBy(view):
            alsoProvides(view, IViewView)

        # finally, you need the name of the manager you want to find
        manager_name = 'plone.contentviews'

        # viewlet managers are found by Multi-Adapter lookup
        manager = getMultiAdapter(
            (context, request, view), IViewletManager, manager_name)

        # calling update() on a manager causes it to set up its viewlets
        manager.update()

        all_viewlets = manager.viewlets
        for viewlet in all_viewlets:
            if viewlet.__name__ == u"plone.contentactions":
                return viewlet.render()


class View(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')

    def update(self):
        """Redirect to @@articles view.

        XXX: this might be problematic, since sometimes we might want to
        get to the article itself.
        """
        portal = api.portal.get()
        return self.request.response.redirect(
            '{0}/@@articles/{1}'.format(
                portal.absolute_url(), self.context.id
            )
        )


class BaseView(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('base-view')
