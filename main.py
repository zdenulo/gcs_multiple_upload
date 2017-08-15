#!/usr/bin/env python

import os
import time
import json
import datetime
import webapp2
import jinja2
from google.cloud import storage

from google.appengine.ext import ndb

from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

client = storage.Client().from_service_account_json(os.environ['SERVICE_JSON_FILE'])
bucket = storage.Bucket(client, os.environ['BUCKET_NAME'])

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class FileModel(ndb.Model):
    filename = ndb.StringProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_updated = ndb.DateTimeProperty(auto_now=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        """Renders main page"""
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class SignedUrlHandler(webapp2.RequestHandler):
    def get(self):
        """Generates signed url to which data will be uploaded. Creates entity in database and saves filename
        Returns json data with url and entity key
        """
        filename = self.request.get('filename', 'noname_{}'.format(int(time.time())))
        content_type = self.request.get('content_type', '')
        file_blob = bucket.blob(filename, chunk_size=262144 * 5)
        url = file_blob.generate_signed_url(datetime.datetime.now() + datetime.timedelta(hours=2), method='PUT',
                                            content_type=content_type)
        file_upload = FileModel(filename=filename)
        file_upload.put()
        key_safe = file_upload.key.urlsafe()
        data = {'url': url, 'key': key_safe}
        self.response.write(json.dumps(data))


class PostUploadHandler(webapp2.RequestHandler):
    def post(self):
        """After upload is completed, this handler can be triggered to do some post processing"""
        key = self.request.params.get('key')
        file_obj = ndb.Key(urlsafe=key).get()
        # do something with it


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/get_signed_url/', SignedUrlHandler),
    ('/postdownload/', PostUploadHandler)
], debug=True)
