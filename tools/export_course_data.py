#!/usr/bin/env python
# encoding: utf-8
"""
export_course_data.py

Created by Brady Law on 2011-01-16.
Copyright (c) 2011 Brady Law. All rights reserved.
"""

import sys
import getopt
import json
import csv

import testudo

help_message = '''
Testudo Course Data Exporter:
Options:
    -h\tHelp
    -q\tQuiet
    -i [file]\tInput json file
    -o [file]\tOutput json file
    -d [dept]\tLimit to specific department
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hoid:q", ["help","output=","input_json_data=","dept="])
        except getopt.error, msg:
            raise Usage(msg)
            
        verbose= True
        output = 'data/course_data.json'
        json_data = None
        dept = None
        
        # option processing
        for option, value in opts:
            if option == "-q":
                verbose = False
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-i", "--input_json_data"):
                json_data = value
            if option in ("-o", "--output"):
                output = value
            if option in ("-d", "--dept"):
                dept = value
            
        c = testudo.crawler(term='201101', verbose=verbose)
        if json_data:
            # Load exising JSON data (faster)
            courses = json.load(open(json_data, 'rb'))
        else:
            # Fetch course data from server
            if dept:
                courses = c.get_courses(dept=dept)
            else:
                courses = c.get_all_courses()
            json.dump(courses, open(output, 'wb'), indent=2)
        
        if csv:
            course_writer = csv.writer(open('data/courses.csv', 'wb'), delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            section_writer = csv.writer(open('data/sections.csv', 'wb'), delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            class_time_writer = csv.writer(open('data/class_times.csv', 'wb'), delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            for c in courses:
                if c['sections']:
                    for s in c['sections']:
                        if s['class_times']:
                            for ct in s['class_times']:
                                class_time_writer.writerow([c['code'], s['section']] + ct.values())
                        del s['class_times']
                        section_writer.writerow([c['code']] + s.values())
                del c['sections']
                course_writer.writerow(c.values())
                    
        
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
