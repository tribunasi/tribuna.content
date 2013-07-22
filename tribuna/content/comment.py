from plone.app.discussion.interfaces import IComment
from plone.app.discussion.comment import Comment
from zope.component.factory import Factory
from plone.indexer import indexer
from zope.interface import implements
from plone import api
from rwproperty import getproperty, setproperty
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from five import grok


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


@grok.subscribe(IComment, IObjectAddedEvent)
def add_tags(comment, event):
    value = comment.subject
    if value is None:
        value = []
    #old_tags = set(self.context.Subject())

    # Get all 'new' tags
    catalog = api.portal.get_tool(name='portal_catalog')
    items = catalog({
        'portal_type': 'tribuna.content.tag',
    })
    titles = set(i.Title for i in items)
    titles = [j.lower().replace(' ', '') for j in titles]

    # Compare tags with the one already in our system, if they're the
    # "same" (lower and ignore spaces), use those tags
    new_titles = [(it.Title, it.Title.lower().replace(' ', ''))
                  for it in items]
    for val in value[:]:
        for tup in new_titles:
            if val.lower().replace(' ', '') == tup[-1]:
                #if val in value:
                value.remove(val)
                value.append(tup[0])

    # Change all "same" (as above) tags to the first appearance
    counter = []
    for val in value[:]:
        if val.lower().replace(' ', '') in counter:
            value.remove(val)
        else:
            counter.append(val.lower().replace(' ', ''))

    new_value = [k for k in value
                 if k.lower().replace(' ', '') not in titles]

    # Set Subject as an union of tags in tags_old and tags_new but use the
    # titles that are already there, don't make new ones (above)


    site = api.portal.get()
    with api.env.adopt_roles(['Site Administrator']):
        comment.setSubject(tuple(value))
        for title in new_value:
            obj = api.content.create(
                type='tribuna.content.tag',
                title=title,
                container=site['tags'])
            api.content.transition(obj=obj, transition='submit')
