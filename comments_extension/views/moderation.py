from __future__ import absolute_import
from django.conf import settings
from django.http import HttpResponse
from django.contrib import comments
from django.contrib.comments import signals
from django.contrib.comments.views.utils import confirmation_view, next_redirect
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from comments_extension.forms import CommentEditForm


class CommentEditBadRequest(CommentPostBadRequest):
    """
    Response returned when a comment edit is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(CommentEditBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})


@csrf_protect
@require_POST
@permission_required("comments.can_moderate")
def edit(request, comment_id, next=None):
    """
    Edit a comment.
    
    Requires HTTP POST and "can moderate comments" permission.
    Users can also only edit comments they own, unless they are given
    "comments.change_comment" on this specific comment object.
    
    If ``POST['submit'] == "preview"`` or there are errors,
    a preview template ``comments/preview.html`` will be rendered.
    
    Templates: `comments/edit.html`,
    Context:
        comment
            the `comments.comment` object to be edited.
    """
    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)
    
    # Check permissions
    if not (request.user == comment.user or request.user.has_perms(["comments.change_comment"], comment)):
        # Return a 401 error if user has not permission to edit this comment.
        return HttpResponse("Unauthorized", status=401)

    perform_edit(request, comment)
    return next_redirect(request.POST.copy(), next, edit_done, c=comment.pk)
    
 
def perform_edit(request, comment):
    """
    Actually perform the editing of comment from a request.
    """
    MODERATOR_EDITED = "moderator edited"
    
    form = CommentEditForm(request.POST, instance=comment)
    if form.is_valid():
        
        flag, created = comments.models.CommentFlag.objects.get_or_create(
            comment = form.instance,
            user = request.user,
            flag = MODERATOR_EDITED
        )
        
        form.instance.is_removed = False
        form.save()
        
        signals.comment_was_flagged.send(
            sender = comment.__class__,
            comment = comment,
            flag = flag,
            created = created,
            request = request
        )
    

edit_done = confirmation_view(
    template = "comments/edited.html",
    doc = 'Displays a "comment was edited" success page.'
)
