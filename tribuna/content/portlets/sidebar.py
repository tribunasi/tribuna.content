#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Portlet for filterting/searching the content."""

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
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from tribuna.content import _
from tribuna.content.utils import get_articles
from tribuna.content.utils import TagsList
from tribuna.content.utils import TagsListHighlighted

# SimpleTerm(value (actual value), token (request), title (shown in browser))
# tags, sort_on, content_filters, operator


class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    form.widget(tags=CheckBoxFieldWidget)
    tags = schema.List(
        title=_(u"Tags"),
        value_type=schema.Choice(source=TagsListHighlighted()),
        required=False,
        default=[],
    )

    form.widget(all_tags=CheckBoxFieldWidget)
    all_tags = schema.List(
        title=_(u"All tags"),
        value_type=schema.Choice(source=TagsList()),
        required=False,
        default=[],
    )

    sort_on = schema.Choice(
        title=_(u"Type of sorting"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('latest', 'latest', _(u'Latest')),
            SimpleTerm('comments', 'comments', _(u'Nr. of comments')),
        ]),
    )

    form.widget(content_filters=CheckBoxFieldWidget)
    content_filters = schema.List(
        title=_(u"Content filters"),
        value_type=schema.Choice(source=SimpleVocabulary([
            SimpleTerm('article', 'article', _(u'Article')),
            SimpleTerm('comment', 'comment', _(u'Comment')),
            SimpleTerm('image', 'image', _(u'Image')),
        ])),
        required=False,
    )


@form.default_value(field=ISidebarForm['tags'])
def default_tags(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["tags"]
    else:
        return []


@form.default_value(field=ISidebarForm['all_tags'])
def default_all_tags(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["tags"]
    else:
        return []


@form.default_value(field=ISidebarForm['sort_on'])
def default_sort_on(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["sort_on"]
    else:
        return "latest"


@form.default_value(field=ISidebarForm['content_filters'])
def default_content_filters(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["content_filters"]
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

    label = _(u"Select appropriate tags")
    description = _(u"Tags selection form")

    @button.buttonAndHandler(_(u'Filter'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set("portlet_data", data)
        session["search-view"] = {}
        session["search-view"]['active'] = False
        get_articles(session)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/home".format(url))

    @button.buttonAndHandler(_(u'Text'))
    def handleApply(self, action):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set('view_type', 'text')
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u'Drag'))
    def handleApply(self, action):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set('view_type', 'drag')
        self.request.response.redirect(self.request.getURL())


class ISidebarPortlet(IPortletDataProvider):
    pass


class Assignment(base.Assignment):
    implements(ISidebarPortlet)

    heading = _(u"Sidebar navigation")
    description = _(u"Use this portlet for tag navigation.")

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
