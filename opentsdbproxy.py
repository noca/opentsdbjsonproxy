#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xiaoyunpeng@wandoujia.com
@date: Wed Dec 25 18:40:57 2013

Copyright (c) 2012, Wandou Labs and/or its affiliates. All rights reserved.
WANDOU LABS PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
"""

ODBHOST="http://127.0.0.1:4242"

import sys

import tornado.web
import tornado.httpclient
import json


class ProxyHandler(tornado.web.RequestHandler):
    """
    """
    @tornado.web.asynchronous
    def get(self):
        chart_type = self.get_argument("charttype", "")

        http = tornado.httpclient.AsyncHTTPClient()

        callback = self._decorate_data
        if chart_type == "highcharts":
            callback = self._highcharts_decorate_data
        elif chart_type == "highcharts2":
            callback = self._highcharts2_decorate_data
        http.fetch(ODBHOST+self.request.uri, callback)
        return


    def _dump_data(self, de_data):
        jsonp = self.get_argument("callback", "")
        if jsonp == "":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(de_data))
        else:
            self.set_header("Content-Type", "application/javascript")
            self.write(jsonp + "(" + json.dumps(de_data) + ")")

        self.finish()
        return


    def _decorate_data(self, response):
        if response.code != 200:
            self.set_status(response.code)
            self.finish()
            return

        de_data = []
        data = response.body
        for line in data.split("\n"):
            line = line.strip()
            if line == "":
                continue
            vs = line.split(" ")
            odata = {
                "metric": vs[0],
                "timestamp": vs[1],
                "value": vs[2],
                "tags": [{x.split("=")[0]:x.split("=")[1]} for x in vs[3:] ]
            }
            de_data.append(odata)

        self._dump_data(de_data)
        return

    def _highcharts_decorate_data(self, response):
        if response.code != 200:
            self.set_status(response.code)
            self.finish()
            return

        de_data = dict()

        data = response.body
        for line in data.split("\n"):
            line = line.strip()
            if line == "":
                continue
            vs = line.split(" ")
            metric = vs[0] + "{" + ",".join(vs[3:]) + "}"
            if metric not in de_data.keys():
                de_data[metric] = {
                    "name": metric,
                    "pointInterval":0,
                    "pointStart": sys.maxint,
                    "pointEnd":0,
                    "data":list()
                }

            de_data[metric]['data'].append(float(vs[2]))
            timestamp = int(vs[1])
            de_data[metric]['pointStart'] = timestamp if timestamp < de_data[metric]['pointStart'] else de_data[metric]['pointStart']
            de_data[metric]['pointEnd'] = timestamp if timestamp > de_data[metric]['pointEnd'] else de_data[metric]['pointEnd']


        hcde_data = list()
        for k,v in de_data.items():
            v['pointInterval'] = 1000 * (v["pointEnd"] - v['pointStart'])/len(v['data'])
            v['pointStart'] = (v['pointStart'] + 8*3600) * 1000
            hcde_data.append(v)

        self._dump_data(hcde_data)
        return

    def _highcharts2_decorate_data(self, response):
        if response.code != 200:
            self.set_status(response.code)
            self.finish()
            return

        de_data = dict()

        data = response.body
        for line in data.split("\n"):
            line = line.strip()
            if line == "":
                continue
            vs = line.split(" ")
            metric = vs[0] + "{" + ",".join(vs[3:]) + "}"
            if metric not in de_data.keys():
                de_data[metric] = {
                    "name": metric,
                    "data":list()
                }

            de_data[metric]['data'].append([(int(vs[1]) + 8*3600) *1000, float(vs[2])])

        hcde_data = list()
        for k,v in de_data.items():
            hcde_data.append(v)

        self._dump_data(hcde_data)
        return



dispatch_pattern = [
    (r"/q", ProxyHandler),
]


application = tornado.web.Application(dispatch_pattern)

if __name__ == "__main__":
    application.listen(5242, "0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
