#!/usr/bin/env python
# encoding: utf-8
"""
testudo_crawl.py

Created by Brady Law on 2011-01-16.
Copyright (c) 2011 Unknown. All rights reserved.
"""

import re
import urllib
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
    def __init__(self, term, verbose=False):
        self.term = term
        if verbose:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.WARNING)
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
    'id' : 16141,
    'title' : 'Introduction to Computer Programming via the Web',
    'credits' : 3,
    'grade' : 'REG/P-F/AUD',
    'description' : 'Corequisite: MATH140 and permission of department. Not open to students \
        who have completed CMSC114. Introduction to programming and computer science. Emphasizes \
        understanding and implementation of applications using object-oriented techniques. Develops \
        skills such as program design and testing as well as implementation of programs using a \
        graphical IDE. Programming done in Java. '
    
    'teacher' : 'B Dole.',
    'section' : '0001',
    
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
        course_pattern = re.compile(r"""
                <font\sface="arial,helvetica"\ssize=-1>\s*
                <b>(?P<code>.*)<\/b>\s*
                (<i>(?P<permreq>.*)<\/i>\s*)?
                <b>(?P<title>.*);<\/b>\s*
                <b>\s*\((?P<credits>.*)\s+credits?\)\s*</b>\s*
                Grade\s*Method:\s*(?P<grade_method>.*)\.\s*
                (?P<details>.*)\s*
                <br>\s*
                (?P<description>[\s\S]*?)
                <\/font>\s*
                (<br>\s*)?
                
                # Get section data in <blockquote> tags for additional parsing
                (<blockquote>(?P<section_data>[\s\S]*?)<\/blockquote>)?
                """, re.IGNORECASE | re.VERBOSE)
            
        courses = list()
        for m in course_pattern.finditer(response):
            course = dict(
                    code=clean_and_trim(m.group('code')),
                    title=clean_and_trim(m.group('title')),
                    permreq=clean_and_trim(m.group('permreq')),
                    credits=clean_and_trim(m.group('credits')),
                    grade_method=clean_and_trim(m.group('grade_method')),
                    details=clean_and_trim(m.group('details')),
                    description=clean_and_trim(m.group('description')),
                    sections=self.parse_section_data(section_data=m.group('section_data')) \
                            if m.group('section_data') else None
                    )
            courses.append(course)

        if self.verbose:
            logger.info('%d courses downloaded for %s.' % (len(courses), dept))
            
        return courses
    
    def parse_section_data(self, section_data):
        section_pattern = re.compile(r"""
                <dl>\s*
                (?P<section>\d{4})\((?P<course_id>\d{5})\)\s*
                (<a\s.*?>\s*)?
                (?P<teacher>[\s\S]+?)\s*
                (</a>\s*)?
                \((FULL:\s*)?Seats=(?P<seats>\d+),\sOpen=(?P<open>\d+),\sWaitlist=(?P<waitlist>\d+)\)
                (?P<class_time_data>[\s\S]*?)
                <\/dl>
                """, re.IGNORECASE | re.VERBOSE)
                
        class_time_pattern = re.compile(r"""
            <dd>
            (?P<days>[MWFTuh]+)
            [.\s]*
            (?P<start_time>\d{1,2}:\d{2}[apm]{2})-\s*(?P<end_time>\d{1,2}:\d{2}[apm]{2})
            .*?
            </dd>
        """, re.IGNORECASE | re.VERBOSE)
        
        sections = list()   
        for s in section_pattern.finditer(section_data):
            class_times = list()
            if s.group('class_time_data'):
                for ct in class_time_pattern.finditer(s.group('class_time_data')):
                    class_times.append(ct.groupdict())
                
            sections.append(dict(
                section=clean_and_trim(s.group('section')),
                course_id=clean_and_trim(s.group('course_id')),
                teacher=clean_and_trim(s.group('teacher')),
                seats=clean_and_trim(s.group('seats')),
                open=clean_and_trim(s.group('open')),
                waitlist=clean_and_trim(s.group('waitlist')),
                class_times=class_times
            ))
            
        return sections
        
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
