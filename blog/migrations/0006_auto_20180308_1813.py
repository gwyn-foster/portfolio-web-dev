# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-08 18:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmedia', '0001_initial'),
        ('blog', '0005_remove_pocpage_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='pocpage',
            name='media',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailmedia.Media'),
        ),
        migrations.AlterField(
            model_name='pocpage',
            name='body',
            field=wagtail.core.fields.StreamField((('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('document', wagtail.documents.blocks.DocumentChooserBlock()))),
        ),
    ]
