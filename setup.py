#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "django-comments-extension",
    version = "1.2",
    description = "contrib.comments extensions.",
    long_description = "Provides edit functionality to the contrib.comments framework",
    keywords = "django edit comments",
    license = open("LICENSE.md").read(),
    author = "Rolf Håvard Blindheim",
    author_email = "rhblind@gmail.com",
    url = "https://github.com/rhblind/django-comments-extension",
    packages = [
        "comments_extension",
        "comments_extension.views",
        "comments_extension.templatetags"
    ],
    package_data = {
        "comments_extension": [
            "templates/comments/*.html",
        ]
    },
    classifiers = [
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
