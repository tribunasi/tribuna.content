from persistent import Persistent

from z3c.form.field import Fields

from zope import interface
from zope import schema

from zope.annotation import factory
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.z3cform.fieldsets import extensible
from plone.directives import form
from plone.app.discussion.browser.comments import CommentForm
from tribuna.content.comment import Comment
from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget

# Interface to define the fields we want to add to the comment form.
class ICommentExtenderFields(Interface):
    form.widget(subject=TokenInputFieldWidget)
    subject = schema.List(
        title=(u"Categories"),
        value_type=schema.TextLine(),
        default=[],
        required=False
    )

# Persistent class that implements the ICommentExtenderFields interface
class CommentExtenderFields(Persistent):
    interface.implements(ICommentExtenderFields)
    adapts(Comment)
    subject = u""

# CommentExtenderFields factory
CommentExtenderFactory = factory(CommentExtenderFields)

# Extending the comment form with the fields defined in the
# ICommentExtenderFields interface.
class CommentExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, CommentForm)

    fields = Fields(ICommentExtenderFields)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        # Add the fields defined in ICommentExtenderFields to the form.
        self.add(ICommentExtenderFields, prefix="")
        # Move the website field to the top of the comment form.
        self.move('subject', before='text', prefix="")
