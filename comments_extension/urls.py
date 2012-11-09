from django.conf.urls import patterns, url

urlpatterns = patterns("comments_extension.views",
    url(r"^edit/(\d+)/$", view="moderation.edit", name="comments-edit"),
    url(r"^edited/$", view="moderation.edit_done", name="comments-edit-done"),
)
