#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plone.app.discussion.interfaces import IComment
from plone.app.discussion.comment import Comment
from zope.component.factory import Factory
from plone.indexer import indexer
from zope.interface import implements
from plone import api
#from rwproperty import getproperty, setproperty
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from five import grok

from tribuna.content.utils import our_unicode


class TribunaComment(Comment):
    implements(IComment)
    subject = None

    def setSubject(self, subject):
        self.subject = subject

    # @setproperty
    # def subject(self, value):
    #
TribunaCommentFactory = Factory(Comment)


@indexer(IComment)
def subject(object):
    return object.subject


@grok.subscribe(IComment, IObjectCreatedEvent)
def add_tags(comment, event):
    value = comment.subject
    if value is None:
        value = []
    #old_tags = set(self.context.Subject())

    # Get all 'new' tags
    # XXX
    # FIX
    with api.env.adopt_user('tags_user'):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog({
            'portal_type': 'tribuna.content.tag',
        })

        # Compare tags with the one already in our system, if they're the
        # "same" (lower and ignore spaces), use those tags
        titles = dict(
            (our_unicode(it.Title).lower().replace(' ', ''), it.Title)
            for it in items
        )

        dict_value = {}
        for it in value:
            foo = our_unicode(it).lower().replace(' ', '')
            if foo not in dict_value.keys():
                dict_value[foo] = it

        new_value = []
        added_values = []

        for key, val in dict_value.items():
            if key in titles.keys():
                new_value.append(our_unicode(titles[key]))
            else:
                new_value.append(our_unicode(val))
                added_values.append(our_unicode(val))

        site = api.portal.get()
        comment.subject = new_value
        for title in added_values:
            obj = api.content.create(
                type='tribuna.content.tag',
                title=title,
                description="",
                highlight_in_navigation=False,
                container=site['tags'])
            api.content.transition(obj=obj, transition='submit')
