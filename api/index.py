#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys

# 添加父目录到路径以导入 guessitrest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, make_response
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
import guessit
from guessit.jsonutils import GuessitEncoder

# 读取版本信息
here = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(here, '..', 'guessitrest', '__version__.py')
about = {}
if os.path.exists(version_file):
    with open(version_file, 'r') as f:
        exec(f.read(), about)
    __version__ = about.get('__version__', 'unknown')
else:
    __version__ = 'unknown'

app = Flask(__name__)
CORS(app)
api = Api(app)

@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=GuessitEncoder, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp

class GuessIt(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='store', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()
        return guessit.guessit(args.filename, args.options)

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')

class GuessItList(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='append', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()

        ret = []
        for filename in args.filename:
            ret.append(guessit.guessit(filename, args.options))
        return ret

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')

class GuessItVersion(Resource):
    def get(self):
        return {'guessit': guessit.__version__, 'rest': __version__}

api.add_resource(GuessIt, '/')
api.add_resource(GuessItList, '/list/')
api.add_resource(GuessItVersion, '/version/')
