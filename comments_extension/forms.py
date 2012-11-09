from django import forms
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.forms import COMMENT_MAX_LENGTH
from django.utils.text import get_text_list
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _


class CommentEditForm(forms.ModelForm):
    """
    ModelForm for the comment
    """
    def __init__(self, *args, **kwargs):
        super(CommentEditForm, self).__init__(*args, **kwargs)
        self.fields["user_name"].widget.attrs["readonly"] = "readonly"
        self.fields["user_email"].widget.attrs["readonly"] = "readonly"
        self.fields["user_url"].widget.attrs["placeholder"] = "Homepage"
        
    user_name = forms.CharField(label=_("Name"), max_length=50)
    user_email = forms.EmailField(label=_("Email address"))
    user_url = forms.URLField(label=_("URL"), required=False)
    comment = forms.CharField(label=_("Comment"), widget=forms.Textarea,
                                    max_length=COMMENT_MAX_LENGTH)
    
    class Meta:
        model = Comment
        fields = ("user_name", "user_email", "user_url", "comment")
    
    # taken from django.contrib.comments.forms.CommentDetailsForm
    def clean_comment(self):
        """
        If COMMENTS_ALLOW_PROFANITIES is False, check that the comment doesn't
        contain anything in PROFANITIES_LIST.
        """
        comment = self.cleaned_data["comment"]
        if settings.COMMENTS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in comment.lower()]
            if bad_words:
                raise forms.ValidationError(ungettext(
                    "Watch your mouth! The word %s is not allowed here.",
                    "Watch your mouth! The words %s are not allowed here.",
                    len(bad_words)) % get_text_list(
                        ["'%s%s%s'" % (i[0], "-" * (len(i) - 2), i[-1])
                         for i in bad_words], ugettext("and")))
        return comment
