# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Captcha'
        db.create_table('captcha_captcha', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('category', self.gf('django.db.models.fields.IntegerField')()),
            ('image_hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('label_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('add_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('captcha', ['Captcha'])

        # Adding model 'LabelLog'
        db.create_table('captcha_labellog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('captcha', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['captcha.Captcha'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('add_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('captcha', ['LabelLog'])


    def backwards(self, orm):
        # Deleting model 'Captcha'
        db.delete_table('captcha_captcha')

        # Deleting model 'LabelLog'
        db.delete_table('captcha_labellog')


    models = {
        'captcha.captcha': {
            'Meta': {'object_name': 'Captcha'},
            'add_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'label_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'captcha.labellog': {
            'Meta': {'object_name': 'LabelLog'},
            'add_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'captcha': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['captcha.Captcha']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['captcha']