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

class Crawler:
    base_url = 'http://www.sis.umd.edu/bin/soc'
    
    """ Testudo Regular Expressions:
    Cheatsheet:
        (?P<var>...)    Variable named "var".
        .               Any char except \n.
        [\s\S]          Any char.
        *               Match as much as possible
        *?              Match as little as possible.
    """
    
    """ Simple Course Pattern:
        Grabs only the course code in an effort to be as simple as possible. This is used
        for testing that the full pattern (course_pattern) is correct.
    """
    simple_course_columns = ['code']
    simple_course_pattern = re.compile(r"""
            <font\sface="arial,helvetica"\ssize=-1>\s*
            <b>(?P<code>.*)<\/b>
            """, re.IGNORECASE | re.VERBOSE)
    
    """ Full Course Pattern:
        Grabs all course data, and passes on section data if found for further parsing.
    """
    course_columns = [
            'code',             # ex. CMSC131
            'title',            # ex. Introduction to Computer Programming via the Web
            'permreq',          # ex. PermReq
            'credits',          # ex. 3 credits
            'grade_method',     # ex. REG/P-F/AUD
            'details',          # ex. Corequisite: MATH140 and permission of department...
            'description',      # ex. Introduction to programming and computer science...
            ]
    course_pattern = re.compile(r"""
            <font\sface="arial,helvetica"\ssize=-1>\s*
            <b>(?P<code>.*)<\/b>\s*
            (<i>(?P<permreq>.*)<\/i>\s*)?
            <b>(?P<title>[\s\S]*?);<\/b>\s*
            <b>\s*\((?P<credits>.*)\s+credits?\)\s*</b>\s*
            Grade\s*Method:\s*(?P<grade_method>.*)\.\s*
            (?P<details>[\s\S]*?)\s*
            (<br>\s*
                (?P<description>[\s\S]*?)
            )?
            <\/font>\s*
            (<br>\s*)?

            # Get section data in <blockquote> tags for additional parsing
            (<blockquote>(?P<section_data>[\s\S]*?)<\/blockquote>)?
            """, re.IGNORECASE | re.VERBOSE)
    
    """ Section Pattern:
        Scrapes data for each course section.
    """
    section_columns = [
            'section',
            'course_id',
            'teacher',
            'seats',
            'open',
            'waitlist',
            ]
            # class_time_data
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
    
    """ Class time pattern:
        Scrapes time and location data for each time the section meets.
    """
    class_time_columns = [
            'days',
            'start_time',
            'end_time',
            # 'building',
            # 'room',
            # 'type'
            ]
    class_time_pattern = re.compile(r"""
            <dd>
            (?P<days>[MWFTuh]+)
            [.\s]*
            (?P<start_time>\d{1,2}:\d{2}[apm]{2})-\s*(?P<end_time>\d{1,2}:\d{2}[apm]{2})
            .*?
            </dd>
            """, re.IGNORECASE | re.VERBOSE)
    
    
    def __init__(self, term, verbose=False):
        self.term = term
        if verbose:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.WARNING)
        self.verbose = verbose

    """
    Returns a list of dictionaries representing all departments.
    ex. {
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
    Returns a list of dictionaries representing all courses.
    Args:
        dept - Department to retrieve courses for.
        simple - For testing, use the simpler RegEx search to grab only the course titles.
    """
    def get_courses(self, dept, simple=False):
        if self.verbose:
            logger.info('Downloading %s...' % (dept))
            
        response = self.fetch_courses_page(dept=dept)
        
        pattern = self.course_pattern if not simple else self.simple_course_pattern
        columns = self.course_columns if not simple else self.simple_course_columns
        
        courses = list()
        for m in pattern.finditer(response):
            course_raw_data = m.groupdict()
            course = dict()
            for col in columns:
                course[col] = clean_and_trim(course_raw_data[col])
            course['sections'] = self.parse_section_data(course_raw_data['section_data']) \
                if 'section_data' in course_raw_data else None
            courses.append(course)

        if self.verbose:
            logger.info('%d courses downloaded for %s.' % (len(courses), dept))
            
        return courses
    
    def parse_section_data(self, section_data):
        if not section_data:
            return None
        
        sections = list()
        for s in self.section_pattern.finditer(section_data):
            class_times = list()
            new_section = dict()
            raw_section_data = s.groupdict()

            # Parse the class time data
            if s.group('class_time_data'):
                for ct in self.class_time_pattern.finditer(s.group('class_time_data')):
                    class_times.append(ct.groupdict())

            for col in self.section_columns:
                new_section[col] = clean_and_trim(raw_section_data[col])
                
            new_section['class_times'] = class_times
            sections.append(new_section)
            
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
