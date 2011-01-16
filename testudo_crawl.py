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
import logging

logger = logging.getLogger('testudo_crawler')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

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
        departments = list()
        for match in pattern.finditer(response):
            departments.append(dict(code=match.group(1).strip(), title=match.group(2).strip()))
        
        if self.verbose:
            logger.info('%d departments found.' % len(departments))
            
        return departments
    
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
    
    'c1_building' : 'CSI',
    'c1_room' : 2117,
    'c1_time_start' : '10:00am',
    'c1_time_end' : '10:50am',
    'c1_days' : 'MWF',
    'c1_type' : None,
    
    'c2_building' : 'CSI',
    'c2_room' : 2120,
    'c2_time_start' : '11:00am',
    'c2_time_end' : '11:50am',
    'c2_days' : 'MW',
    'c2_type' : 'Dis',
    
    'c3_building' : None,
    'c3_room' : None,
    'c3_time_start' : None,
    'c3_time_end' : None,
    'c3_days' : None,
    'c3_type' : None,
    
    'start_date' : None, # Example '03/28/11'
    'end_date' : None, # Example '03/28/11'
    
    'seats' : 25,
    'open' : 0,
    'waitlist' : 7,
    }
    """
    def get_courses(self, dept):
        if self.verbose:
            logger.info('Downloading %s...' % (dept))
            
        response = self.fetch_courses_page(dept=dept)
        pattern = re.compile(r"""
                <font\sface="arial,helvetica"\ssize=-1>[\s]*
                <b>(?P<code>.*)<\/b>[\s]*
                (<i>(?P<permreq>.*)<\/i>[\s]*)?                     # optional
                <b>(?P<title>.*);<\/b>[\s]*
                <b>\s*\((?P<credits>.*)\s+credits?\)\s*</b>[\s]*
                Grade\s*Method:\s*(?P<grade_method>.*)\.[\s]*
                <br>[\s]*
                (<i>(?P<requirements>[^<]*)<\/i>[\s]*)?           # optional
                (?P<description>[^<]*)
                <\/font>[\s]*
                """,
                re.IGNORECASE | re.VERBOSE)
        courses = list()
        for m in pattern.finditer(response):
            courses.append(dict(
                    code=clean_and_trim(m.group('code')),
                    title=clean_and_trim(m.group('title')),
                    permreq=clean_and_trim(m.group('permreq')),
                    credits=clean_and_trim(m.group('credits')),
                    grade_method=clean_and_trim(m.group('grade_method')),
                    requirements=clean_and_trim(m.group('requirements')),
                    description=clean_and_trim(m.group('description'))
                    ))

        if self.verbose:
            logger.info('%d courses downloaded for %s.' % (len(courses), dept))
            
        return courses
            
    def fetch_departments_page(self):
        return self.fetch_courses_page(dept='DEPT')
        
    def fetch_courses_page(self, dept):
        params = urllib.urlencode({ 'crs' : dept, 'term' : self.term })
        f = urllib.urlopen(self.base_url + '?%s' % params)
        response = f.read()
        f.close()
        return response
    
    def get_all_courses(self):
        departments = self.get_departments()
        all_courses = list()
        
        d_count = len(departments)
        d_pos = 0
        
        for d in departments:
            d_pos += 1
            logger.info('Dept %d/%d' % (d_pos, d_count))
            all_courses.extend(self.get_courses(dept=d['code']))
            
        if self.verbose:
            logger.info('Done! %d courses found for %d departments.' % (len(all_courses), len(departments)))
            
        return all_courses
        
def clean_and_trim(string):
    if string:
        return string.replace('\n', ' ').strip()
    else:
        return None

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
        found = False
        correct_course = {
        'code': 'CMSC131',
        'requirements': 'Corequisite: MATH140 and permission of department. Not open to students who have completed CMSC114.',
        'description': 'Introduction to programming and computer science. Emphasizes understanding and implementation of applications using object-oriented techniques. Develops skills such as program design and testing as well as implementation of programs using a graphical IDE. Programming done in Java.',
        'title': 'Object-Oriented Programming I',
        'grade_method': 'REG',
        'credits': '4',
        'permreq': '(PermReq)'}
        
        for c in courses:
            logger.debug(c)
            
            if c['code'] == correct_course['code']:
                found = True
                assert len(correct_course) == len(c)
                for k, v in correct_course.items():
                    assert c[k] == v, 'Course check failed!\nGenerated:\t%s\nCorrect:\t%s' % (c[k], v)
            assert len(courses) > 20
        assert found
    
    def test_get_all_courses(self):
        courses = self.crawler.get_all_courses()
        logger.debug(courses)
        
if __name__ == "__main__":
    unittest.main()
