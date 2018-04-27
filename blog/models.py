
from __future__ import unicode_literals

import datetime
from datetime import date

from django import forms
from django.db import models

from django.urls import reverse
from django.utils.dateformat import DateFormat
from django.utils.formats import date_format
from django.utils.html import format_html
# Create your models here.
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.blocks import StructBlock, EmailBlock
from wagtail.snippets.models import register_snippet


from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtailmedia.edit_handlers import MediaChooserPanel

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager

from taggit.models import TaggedItemBase, Tag as TaggitTag
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from wagtail.embeds.blocks import EmbedBlock
from wagtail.documents.blocks import DocumentChooserBlock



class WhatWeDoPage(Page):
    description = RichTextField(max_length=1000, blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('photo'),
    ]


class TagsListPage(Page):
    description = models.CharField(max_length=180)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
    ]

class PocIndexPage(RoutablePageMixin, Page):

    description = RichTextField(max_length=150, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
    ]
    def get_posts(self):
        return PocPage.objects.descendant_of(self).live().order_by('-date')


    def get_context(self, request, *args, **kwargs):
        context=super(PocIndexPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.posts
        context['poc_index_page'] = self
        context['search_type'] = getattr(self, 'search_type', "")
        context['search_term'] = getattr(self, 'search_term', "")
        return context


    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, **kwargs)

     # will override the default Page serving mechanism
    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_posts().filter(date__year=year)
        self.search_type = 'date'
        self.search_term = year
        if month:
            self.posts = self.posts.filter(date__month=month)
            df = DateFormat(date(int(year), int(month), 1))
            self.search_term = df.format('F Y')
        if day:
            self.posts = self.posts.filter(date__day=day)
            self.search_term = date_format(date(int(year), int(month), int(day)))
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        poc_page = self.get_posts().filter(slug=slug).first()
        if not poc_page:
            raise Http404
        return Page.serve(poc_page, request, *args, **kwargs)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        print(category)

        self.posts = self.get_posts().filter(categories__slug=category)
        print (self.posts)
        return Page.serve(self, request, *args, **kwargs)



class PocPage(Page):

    author = models.CharField(max_length=100, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)
    date = models.DateTimeField(verbose_name="Post date", default=datetime.datetime.today)
    description = models.CharField(max_length=180, help_text="A quick summary of your article <180 characters")
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentChooserBlock()),
    ])
    video = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',

    )

    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The photo that will show on the main page',
    )

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        FieldPanel('description'),
        StreamFieldPanel('body'),
        FieldPanel('video'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),

    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),

    ]

    @property
    def poc_index_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(PocPage, self).get_context(request, *args, **kwargs)
        context['poc_index_page'] = self.poc_index_page
        context['post'] = self
        return context





class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('PocPage', related_name='poc_tags')

@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy=True

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class OurTeamIndexPage(Page):
    description = models.CharField(max_length=180)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
    ]

class TeamMemberPage(Page):

    first_name = models.CharField(max_length=300)
    surname = models.CharField(max_length=300)
    job_title = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=300)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    biography = models.CharField(max_length=1000)



    content_panels = Page.content_panels + [
        FieldPanel('first_name'),
        FieldPanel('surname'),
        FieldPanel('job_title'),
        FieldPanel('phone_number'),
        FieldPanel('email'),
        FieldPanel('biography'),
        ImageChooserPanel('photo'),
    ]

class ExcitedPage(Page):
    description = models.CharField(max_length= 500)
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel('icon'),
        FieldPanel('description'),
    ]
