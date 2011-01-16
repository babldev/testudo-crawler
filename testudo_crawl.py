#!/usr/bin/env python
# encoding: utf-8
"""
testudo_crawl.py

Created by Brady Law on 2011-01-16.
Copyright (c) 2011 Unknown. All rights reserved.
"""

import sys
import os
import re
import urllib
import unittest

class testudocrawler:
    base_url = 'http://www.sis.umd.edu/bin/soc'
    def __init__(self, term, verbose=True):
        self.term = term
        self.verbose = verbose

    """
    Returns a LIST of DICTIONARIES of the form:
    {
    'code' : 'AASP',
    'title' : 'African American Studies'
    }
    """
    def get_departments(self):
        response = self.fetch_departments_page()
        pattern = re.compile('<a href=soc.*>(.*)</a>(.*)<br>', re.I)
        parsed = list()
        for match in pattern.finditer(response):
            parsed.append(dict(code=match.group(1).strip(), title=match.group(2).strip()))
        return parsed
    
    """
    Returns a LIST of DICTIONARIES of the form:
    {
    'code' : 'CMSC131',
    'section' : '0001',
    'id' : 16141,
    'title' : 'Introduction to Computer Programming via the Web',
    'credits' : 3,
    'grade' : 'REG/P-F/AUD',
    'description' : 'Corequisite: MATH140 and permission of department. Not open to students \
        who have completed CMSC114. Introduction to programming and computer science. Emphasizes \
        understanding and implementation of applications using object-oriented techniques. Develops \
        skills such as program design and testing as well as implementation of programs using a \
        graphical IDE. Programming done in Java. '
    
    'building' : 'CSI',
    'room' : 2117,
    'time_start' : '10:00am',
    'time_end' : '10:50am',
    'days' : 'MWF',
    
    'dis_building' : 'CSI'
    'dis_room' : 2120,
    'dis_time_start' : '11:00am',
    'dis_time_end' : '11:50am',
    'dis_days' : 'MW',
    
    'seats' : 25,
    'open' : 0,
    'waitlist' : 7,
    }
    """
    def get_courses(self, dept):
        response = self.fetch_courses_page(dept=dept)
        return None
        
    def fetch_departments_page(self):
        return self.fetch_courses_page(dept='DEPT')
        
    def fetch_courses_page(self, dept):
        params = urllib.urlencode({ 'crs' : dept, 'term' : self.term })
        f = urllib.urlopen(self.base_url + '?%s' % params)
        response = f.read()
        f.close()
        return response


class testudocrawler_tests(unittest.TestCase):
    def setUp(self):
        self.crawler = testudocrawler(term='201101')
        pass
    
    def test_fetch_departments_page(self):
        response = self.crawler.fetch_departments_page()
        assert response is not None
        assert len(response) > 20
        assert response.find('CMSC') > 0
    
    def test_get_departments(self):
        departments = self.crawler.get_departments()
        assert departments is not None
        assert len(departments) > 20
        assert dict(code='CMSC', title='Computer Science') in departments
    
    def test_fetch_courses_page(self):
        response = self.crawler.fetch_courses_page('CMSC')
        assert response is not None
        assert len(response) > 20
        assert response.find('Object-Oriented Programming I') > 0
    
    def test_get_courses(self):
        courses = self.crawler.get_courses('CMSC')
        assert courses is not None
        assert len(courses) > 20
        assert dict(code='CMSC', title='Computer Science') in courses

if __name__ == "__main__":
    unittest.main()
