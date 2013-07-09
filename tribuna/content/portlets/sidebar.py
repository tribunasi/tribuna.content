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
from tribuna.content.utils import countSame
from tribuna.content.utils import TagsList
from tribuna.content.utils import TagsListHighlighted

# Number of items to display
LIMIT = 15

# SimpleTerm(value (actual value), token (request), title (shown in browser))
# tags, sort_on, content_filters, operator


def articles(session):
    """Return a list of all articles depending on the specified filters

    XXX: Treba dodati se:
          - portal_type: osnova so vsi tipi
    """

    catalog = api.portal.get_tool(name='portal_catalog')
    portal_type = ["tribuna.content.article"]
    review_state = "published"
    sort_on = "Date"
    query = None
    operator = "or"

    if('portlet_data' not in session.keys() or
       session['portlet_data']['tags'] == []):
        all_content = catalog(
            portal_type=portal_type,
            locked_on_home=True,
            review_state=review_state,
            sort_on=sort_on,
            sort_limit=LIMIT
        )[:LIMIT]

        currentLen = len(all_content)

        if currentLen < LIMIT:
            all_content += catalog(
                portal_type=portal_type,
                locked_on_home=False,
                review_state=review_state,
                sort_on=sort_on,
                sort_limit=(LIMIT - currentLen)
            )[:(LIMIT - currentLen)]

        if not all_content:
            session.set('content_list', [])
            session.set('content_list',
                        [content.getObject() for content in all_content])
            return True

    # portal_type
    if session['portlet_data']['content_filters']:
        portal_type = []
        for i in session['portlet_data']['content_filters']:
            if(i == 'articles'):
                portal_type.append("tribuna.content.article")
            elif(i == 'comments'):
                pass
            elif(i == 'images'):
                pass

    # sort_on
    tmp = session['portlet_data']['sort_on']
    if tmp == 'latest':
        sort_on = 'Date'
    elif tmp == 'alphabetical':
        sort_on = 'sortable_title'
    elif tmp == 'comments':
        pass

    sort_order = session['portlet_data']['sort_order']

    all_content = []
    session['portlet_data']['tags'] = \
        list(set(session['portlet_data']['tags'] +
                 session['portlet_data']['all_tags']))

    # if(not session['portlet_data']['tags']):
    #     # Ce ni nicesar pokaze zadnje
    #     # Naj se spremeni v to, da izbira med highlightanimi tagi
    #     all_content = catalog(
    #         portal_type=portal_type,
    #         locked_on_home=True,
    #         review_state=review_state,
    #         sort_on=sort_on,
    #         sort_order=sort_order,
    #         sort_limit=LIMIT
    #     )[:LIMIT]
    #     currentLen = len(all_content)
    #     if currentLen < LIMIT:
    #         all_content += catalog(
    #             portal_type=portal_type,
    #             locked_on_home=False,
    #             review_state=review_state,
    #             sort_on=sort_on,
    #             sort_order=sort_order,
    #             sort_limit=(LIMIT - currentLen)
    #         )[:LIMIT - currentLen]
    # else:
    query = session['portlet_data']['tags']
    # tmp = session['portlet_data']['operator']
    # if(tmp == 'union'):
    #     operator = 'or'
    # elif(tmp == 'intersection'):
    #     operator = 'and'

    all_content = catalog(
        portal_type=portal_type,
        review_state=review_state,
        sort_on=sort_on,
        sort_order=sort_order,
        Subject={'query': query, 'operator': operator},
    )

    all_content = [content for content in all_content]
    all_content.sort(
        key=lambda x: countSame(x.Subject, query), reverse=True)
    all_content = all_content[:LIMIT]

    if not all_content:
        session.set('content_list', [])
    session.set(
        'content_list',
        [content.getObject() for content in all_content]
    )


class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    form.widget(tags=CheckBoxFieldWidget)
    tags = schema.List(
        title=_(u"Tags"),
        value_type=schema.Choice(source=TagsListHighlighted()),
    )

    form.widget(all_tags=CheckBoxFieldWidget)
    all_tags = schema.List(
        title=_(u"All tags"),
        value_type=schema.Choice(source=TagsList()),
    )

    sort_on = schema.Choice(
        title=_(u"Type of sorting"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('alphabetical', 'alphabetical', _(u'Alphabetical')),
            SimpleTerm('comments', 'comments', _(u'Nr. of comments')),
            SimpleTerm('latest', 'latest', _(u'Latest')),
        ]),
    )

    sort_order = schema.Choice(
        title=_(u"Order of sorting"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('ascending', 'ascending', _(u'Ascending')),
            SimpleTerm('descending', 'descending', _(u'Descending')),
        ]),
    )

    form.widget(content_filters=CheckBoxFieldWidget)
    content_filters = schema.List(
        title=_(u"Content filters"),
        value_type=schema.Choice(source=SimpleVocabulary([
            SimpleTerm('articles', 'articles', _(u'Articles')),
            SimpleTerm('comments', 'comments', _(u'Comments')),
            SimpleTerm('images', 'images', _(u'Images')),
        ])),
    )

    # operator = schema.Choice(
    #     title=_(u"How to apply tags"),
    #     vocabulary=SimpleVocabulary([
    #         SimpleTerm('union', 'union', _(u'Union')),
    #         SimpleTerm('intersection', 'intersection', _(u'Intersection')),
    #     ]),
    # )


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


@form.default_value(field=ISidebarForm['sort_order'])
def default_sort_order(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["sort_order"]
    else:
        return "descending"


@form.default_value(field=ISidebarForm['content_filters'])
def default_content_filters(data):
    sdm = data.context.session_data_manager
    session = sdm.getSessionData(create=True)
    if "portlet_data" in session.keys():
        return session["portlet_data"]["content_filters"]
    else:
        return []


# @form.default_value(field=ISidebarForm['operator'])
# def default_operator(data):
#     sdm = data.context.session_data_manager
#     session = sdm.getSessionData(create=True)
#     if("portlet_data" in session.keys()):
#             return session["portlet_data"]["operator"]
#     else:
#         return "union"


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
        articles(session)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/@@home-page".format(url))

    @button.buttonAndHandler(_(u'Text'))
    def handleApply(self, action):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set('view_type', 'text')
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u'Drag\'n\'drop'))
    def handleApply(self, action):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        session.set('view_type', 'drag')
        self.request.response.redirect(self.request.getURL())

    # @button.buttonAndHandler(_(u'Gallery'))
    # def handleApply(self, action):
    #     sdm = self.context.session_data_manager
    #     session = sdm.getSessionData(create=True)
    #     session.set('view_type', 'gallery')
    #     self.request.response.redirect(self.request.getURL())

    # @button.buttonAndHandler('Send-Union')
    # def handleApply(self, action):
    #     self._handleApply(action, True)

    # @button.buttonAndHandler('Send-Intersection')
    # def handleApply(self, action):
    #     self._handleApply(action, False)

    # @button.buttonAndHandler("Cancel")
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
