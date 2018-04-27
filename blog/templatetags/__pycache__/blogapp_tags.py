# -*- coding: utf-8 -*-
import six
from django.template import Library, loader
from django.core.urlresolvers import resolve

from ..models import BlogCategory as Category, Tag

register = Library()

@register.simple_tag()
def post_date_url(post, poc_index_page):
    post_date = post.specific.date
    url = poc_index_page.url + poc_index_page.reverse_subpage(
        'post_by_date_slug',
        args=(
            post_date.year,
            '{0:02}'.format(post_date.month),
            '{0:02}'.format(post_date.day),
            post.slug,
        )
    )
    return url

@register.simple_tag(takes_context=True)
def canonical_url(context, post=None):
    if post and resolve(context.request.path_info).url_name == 'wagtail_serve':
        return context.request.build_absolute_uri(post_date_url(post, post.poc_index_page))
    return context.request.build_absolute_uri()
