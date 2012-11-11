## django-comments-extension ##

A portable app to put extensions for the django comments framework in.


As I needed the ability to edit comments in a project I'm working on, I decided to build an extension to the built-in 
comments framework in Django. I have tried to follow the conventions already in the comments framework, and make it
as clean as possible, but there's always room for improvement.

### List of extensions ###
Currently there's only one extension in this app.

* edit

## Installation ##

    $ git clone https://github.com/rhblind/django-comments-extension.git

or install from the python package index
    
    $ pip install django-comments-extension

### settings.py ###

    INSTALLED_APPS = (
        ...,
        'comments_extension',
        ...
    )

### urls.py ###

    urlpatterns = patterns("",
        ...
        url(r"^comments/", include("django.contrib.comments.urls")),
        url(r"^comments/", include("comments_extension.urls")),
        ...
    )

### templates ###
Use as you would normally use the comments framework

    {% load comments %}
    {% load comments_extension %}

    {% get_comment_list for mymodel as comment_list %}
    {% for comment_obj in comment_list %}
        <h1>Your comment here</h1>        
        {{ comment_obj.comment }}
        
        <h3>Your edit form</h3>

        <!-- Load the comment edit form for this message into the form variable -->
        {% get_comment_edit_form for comment_obj as form %}

        <table>
            <!-- Make sure to pass the `comment_obj` variable into the `comment_edit_form_target`
                 tag to get the correct edit url for this comment -->
            <form action="{% comment_edit_form_target comment_obj %}" method="post">
            {% csrf_token %}
                {{ form }}
                <tr>
                    <td colspan="2">
                        <input type="submit" name="submit" value="Post">
                        <input type="submit" name="preview" value="Preview">
                    </td>
                </tr>
            </form>
        </table>
    {% endfor %}


        
    
    


