#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the issue timeseries renderer for Kibble
"""

import json
import time
import hashlib

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    now = time.time()
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = indata['view']):
            view = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = indata['view'])
            viewList = view['_source']['sourceList']
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*3)) # Default to a 3 month span
    
    interval = indata.get('interval', 'month')
    
    
    ####################################################################
    # ISSUES OPENED                                                    #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'created': {
                                        'from': dateFrom,
                                        'to': dateTo
                                    }
                                }
                            },
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    if viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    
    
    # Get number of opened ones, this period
    query['aggs'] = {
            'commits': {
                'date_histogram': {
                    'field': 'createdDate',
                    'interval': interval
                }                
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )
    
    timeseries = {}
    for bucket in res['aggregations']['commits']['buckets']:
        ts = int(bucket['key'] / 1000)
        count = bucket['doc_count']
        timeseries[ts] = {'opened': count}
        
    
    ####################################################################
    # ISSUES CLOSED                                                    #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'closed': {
                                        'from': dateFrom,
                                        'to': dateTo
                                    }
                                }
                            },
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    if viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    
    
    # Get number of closed ones, this period
    query['aggs'] = {
            'commits': {
                'date_histogram': {
                    'field': 'closedDate',
                    'interval': interval
                }                
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )
    
    for bucket in res['aggregations']['commits']['buckets']:
        ts = int(bucket['key'] / 1000)
        count = bucket['doc_count']
        if not ts in timeseries:
            timeseries[ts] = {'opened': 0, 'closed': count}
        else:
            timeseries[ts]['closed'] = count
    
    ts = []
    for k, v in timeseries.items():
        v['date'] = k
        ts.append(v)
        
    
    JSON_OUT = {
        'widgetType': {
            'chartType': 'line',  # Recommendation for the UI
            'nofill': True
        },
        'timeseries': ts,
        'interval': interval,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)