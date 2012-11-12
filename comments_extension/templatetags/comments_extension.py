from __future__ import absolute_import
from django import template
from django.template.loader import render_to_string
from django.contrib.comments.templatetags.comments import CommentFormNode,\
    BaseCommentNode
import comments_extension


register = template.Library()


class CommentEditFormNode(CommentFormNode):
    """
    Insert a form for the comment model into the context.
    """
    def get_form(self, context):
        obj = self.get_object(context)
        if obj:
            return comments_extension.get_edit_modelform(obj)
        else:
            return None
        

class RenderCommentEditFormNode(CommentFormNode):
    """
    Class method to parse render_comment_edit_form and return a Node
    prefilled with existing data.
    """
    
    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_comment_form and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_comment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype = BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr = parser.compile_filter(tokens[3])
            )
    
    def get_target_ctype_pk(self, context):
        try:
            obj = self.object_expr.resolve(context)
        except template.VariableDoesNotExist:
            return None, None
        return obj.content_type, obj.pk
    
    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/edit.html" % (ctype.app_label, ctype.model),
                "comments/%s/edit.html" % ctype.model,
                "comments/edit.html"
            ]
            context.push()
            form = comments_extension.get_edit_modelform(self.get_object(context))
            formstr = render_to_string(template_search_list, {"form": form}, context)
            context.pop()
            return formstr
        else:
            return ""
        

@register.tag
def get_comment_edit_form(parser, token):
    """
    Get a form object to edit existing comment.
    
    Syntax::
    
        {% get_comment_edit_form for [object] as [varname] %}
        {% get_comment_edit_form for [app].[model] [object_id] as [varname] %}
    """
    return CommentEditFormNode.handle_token(parser, token)


@register.tag
def render_comment_edit_form(parser, token):
    """
    Render the comment edit form (as returned by ``{% render_comment_edit_form %}``)
    through the ``comments/edit.html`` template.

    Syntax::

        {% render_comment_edit_form for [object] %}
        {% render_comment_edit_form for [app].[model] [object_id] %}
    """
    return RenderCommentEditFormNode.handle_token(parser, token)


@register.simple_tag
def comment_edit_form_target(comment):
    """
    Get the target URL for the comment form.

    Example::

        <form action="{% comment_edit_form_target comment %}" method="post">
    """
    return comments_extension.get_edit_form_target(comment)
