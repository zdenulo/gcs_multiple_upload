#!/usr/bin/env python
"""Loads third-party Python libraries.

`appengine_config.py` is automatically loaded when Google App Engine
starts a new instance of your application. This runs before any
WSGI applications specified in app.yaml are loaded.
"""

from google.appengine.ext import vendor
vendor.add('lib')
