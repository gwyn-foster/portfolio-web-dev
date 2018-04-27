from django import template
from django.template import Library, loader
from django.core.urlresolvers import resolve
from ..models import BlogCategory as Category, Tag

register = template.Library()

@register.simple_tag()
def post_date_url(post, poc_index_page):
    post_date = post.date
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

@register.inclusion_tag('blog/components/tags_list.html', takes_context=True)
def tags_list(context, limit=None):
    # poc_index_page = context['poc_index_page']
    # tags = Tag.objects.all()
    # if limit:
    #     tags = tags[:limit]
    return {
        'poc_index_page': context['poc_index_page'],
        'request': context['request'],
        'tags_list': Tag.objects.all()
    }

@register.inclusion_tag('blog/components/categories_list.html', takes_context=True)
def categories_list(context):
    # poc_index_page = context['poc_index_page']
    # categories = Category.objects.all()
    return {
        'poc_index_page': context['poc_index_page'],
        'request': context['request'],
        'categories_list': Category.objects.all()
    }
