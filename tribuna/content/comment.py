from plone.app.discussion.interfaces import IComment
from plone.app.discussion.comment import Comment
from zope.component.factory import Factory
from plone.indexer import indexer
from zope.interface import implements


class TribunaComment(Comment):
    implements(IComment)
    subject = None

    def setSubject(self, subject):
        self.subject = subject

TribunaCommentFactory = Factory(Comment)


@indexer(IComment)
def subject(object):
    return object.subject
