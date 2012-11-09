from __future__ import absolute_import
from django.core import urlresolvers
from django.contrib.comments import get_comment_app, get_comment_app_name,\
    DEFAULT_COMMENTS_APP
from comments_extension.forms import CommentEditForm


def get_edit_form():
    """
    Returns a (new) comment edit form object
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_edit_form"):
        return get_comment_app().get_edit_form()
    else:
        return CommentEditForm
    
    
def get_edit_modelform(comment):
    """
    Returns the comment ModelForm instance
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_edit_modelform"):
        return get_comment_app().get_edit_modelform()
    else:
        return CommentEditForm(instance=comment)


def get_edit_form_target(comment):
    """
    Returns the target URL for the comment edit form submission view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_edit_form_target"):
        return get_comment_app().get_edit_form_target()
    else:
        return urlresolvers.reverse("comments_extension.views.moderation.edit", args=(comment.id,))
