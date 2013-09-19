#!/usr/bin/env python
# -*- coding: utf-8 -*-

from five import grok
from plone import api
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import IComment
from plone.indexer import indexer
from zope.component.factory import Factory
from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

from tribuna.content.utils import our_unicode


class TribunaComment(Comment):
    """ Extending comment clas from plone.app.discussion.comment
        so we can add subject field to our comments"""

    implements(IComment)
    subject = None

    def setSubject(self, subject):
        self.subject = subject

TribunaCommentFactory = Factory(Comment)


@indexer(IComment)
def subject(object):
    """
    Returns subject of our object

    :param    object: current comment
    :type     object: TribunaComment

    :returns: Subject of our object
    :rtype:   str
    """
    return object.subject


@grok.subscribe(IComment, IObjectCreatedEvent)
def add_tags(comment, event):
    """ Method that is called when new comment is added, constructs new
        tags if they are needed and assign them to comment

    :param comment: newly created comment
    :type comment: TribunaComment
    :param event: event that happens on comment creation
    :type event: ObjectCreatedEvent
    """

    value = comment.subject
    if value is None:
        value = []

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


class CommentView(grok.View):
    """View for displaying a comment (loaded with AJAX from mainpage)."""
    grok.context(IComment)
    grok.require('zope2.View')
    grok.name('comment-view')

    def get_article_url(self):
        """
        Get URL of the article this comment belongs to.

        :returns: URL of the article
        :rtype:   String
        """
        unwanted = ['type', 'comment', 'id']

        getArgs = ''
        for name in self.request.form:
            if name not in unwanted:
                getArgs += '&' + name + '=' + self.request.form[name]

        if getArgs:
            getArgs = '?' + getArgs[1:]

        article_url = self.context.portal_url()

        # First parent: Comment
        # Second parent: Discussion
        # Third parent: Article on which we commented
        article_url += '/articles/{0}{1}#{2}'.format(
            self.__parent__.__parent__.__parent__.id,
            getArgs,
            self.request.form.get('id')
        )

        return article_url
