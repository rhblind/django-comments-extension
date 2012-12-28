from __future__ import absolute_import

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.html import escape
from django.contrib import comments
from django.contrib.comments import signals
from django.contrib.comments.views.utils import confirmation_view, next_redirect
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.template.context import RequestContext

import comments_extension


class CommentEditBadRequest(HttpResponseBadRequest):
    """
    Response returned when a comment edit is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(CommentEditBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-edit-debug.html", {"why": why})


@csrf_protect
@require_POST
@user_passes_test(lambda u: u.has_perm("comments.change_comment")
                  or u.has_perm("comment.can_moderate"))
def edit(request, comment_id, next=None):
    """
    Edit a comment.
    
    Requires HTTP POST and "can change comments" or "can moderate comments",
    permission. Users can also only edit comments they own, unless they are
    granted "comments.can_moderate" permissions.
    
    If ``POST['submit'] == "preview"`` or there are errors,
    a preview template ``comments/preview.html`` will be rendered.
    
    Templates: `comments/edit.html`,
    Context:
        comment
            the `comments.comment` object to be edited.
    """
    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)
    
    # Make sure user has correct permissions to change the comment,
    # or return a 401 Unauthorized error.
    if not (request.user == comment.user and request.user.has_perm("comments.change_comment")
            or request.user.has_perm("comments.can_moderate")):
        return HttpResponse("Unauthorized", status=401)
    
    # Populate POST data with all required initial data
    # unless they are already in POST
    data = request.POST.copy()
    if not data.get("user_name", ""):
        data["user_name"] = request.user.get_full_name() or request.user.username
    if not data.get("user_email"):
        data["user_email"] = request.user.email
    
    next = data.get("next", next)
    CommentEditForm = comments_extension.get_edit_form()
    form = CommentEditForm(data, instance=comment)
    
    if form.security_errors():
        # NOTE: security hash fails!
        return CommentEditBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))
    
    # If there are errors, or if a preview is requested
    if form.errors or "preview" in data:
        app_label, model = (form.instance.content_type.app_label, form.instance.content_type.model)
        template_search_list = [
            "comments/%s/%s/edit-preview.html" % (app_label, model),
            "comments/%s/edit-preview.html" % model,
            "comments/edit-preview.html"
        ]
        return render_to_response(
            template_search_list, {
                "comment_obj": comment,
                "comment": form.data.get("comment", ""),
                "form": form,
                "next": next,
            },
            RequestContext(request, {})
        )
        
    # Otherwise, try to save the comment and emit signals
    if form.is_valid():
        MODERATOR_EDITED = "moderator edited"
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
        
        return next_redirect(request.POST.copy(), next, edit_done, c=comment.pk)
    
    else:
        # If we got here, raise Bad Request error.
        return CommentEditBadRequest("Could not complete request!")
        

edit_done = confirmation_view(
    template = "comments/edited.html",
    doc = 'Displays a "comment was edited" success page.'
)
