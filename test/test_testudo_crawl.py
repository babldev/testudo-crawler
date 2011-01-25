#!/usr/bin/env python
# encoding: utf-8

import unittest
import testudo

class testudocrawler_tests(unittest.TestCase):
    def setUp(self):
        self.crawler = testudo.crawler(term='201101', verbose=True)
        pass
    
    def test_parse_section_data(self):
        sample_section_source = """
<font color=#808080 face="Courier New" size=-1><dl> 
0101(16141)
<a href = "http://www.cs.umd.edu/~djacobs/"> 
D. Jacobs</a> (FULL: Seats=25, Open=0, Waitlist=7) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0101">Books</a> 


<dd>MWF.......10:00am-10:50am (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........11:00am-11:50am (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2120) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0102(16142)
<a href = "http://www.cs.umd.edu/~djacobs/"> 
D. Jacobs</a> (FULL: Seats=25, Open=0, Waitlist=5) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0102">Books</a> 


<dd>MWF.......10:00am-10:50am (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........12:00pm-12:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2120) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0201(16143)
<a href = "http://www.cs.umd.edu/~nelson/"> 
N. Padua-Perez</a> (FULL: Seats=25, Open=0, Waitlist=10) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0201">Books</a> 


<dd>MWF.......11:00am-11:50am (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........ 1:00pm- 1:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2118) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0202(16144)
<a href = "http://www.cs.umd.edu/~nelson/"> 
N. Padua-Perez</a> (FULL: Seats=25, Open=0, Waitlist=6) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0202">Books</a> 


<dd>MWF.......11:00am-11:50am (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........ 3:00pm- 3:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2120) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0301(16145)
<a href = "http://www.cs.umd.edu/~egolub"> 
E. Golub</a> (FULL: Seats=25, Open=0, Waitlist=8) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0301">Books</a> 


<dd>MWF.......12:00pm-12:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........ 1:00pm- 1:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2120) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0302(16146)
<a href = "http://www.cs.umd.edu/~egolub"> 
E. Golub</a> (FULL: Seats=25, Open=0, Waitlist=7) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0302">Books</a> 


<dd>MWF.......12:00pm-12:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........ 2:00pm- 2:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2120) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0401(16147)
<a href = "http://www.cs.umd.edu/~egolub"> 
E. Golub</a> (FULL: Seats=25, Open=0, Waitlist=9) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0401">Books</a> 


<dd>MWF....... 1:00pm- 1:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........ 2:00pm- 2:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2118) Dis</dd> 
</dl> 
</b></font> 
<font color=#808080 face="Courier New" size=-1><dl> 
0402(16148)
<a href = "http://www.cs.umd.edu/~egolub"> 
E. Golub</a> (FULL: Seats=25, Open=0, Waitlist=7) <a href="/bin/bookstore?term=201101&crs=CMSC131&sec=0402">Books</a> 


<dd>MWF....... 1:00pm- 1:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2117)</dd> 
<dd>MW........ 3:00pm- 3:50pm (<a href="http://www.umd.edu/CampusMaps/bld_detail.cfm?bld_code=CSI">CSI</a> 2118) Dis</dd> 
</dl> 
</b></font>        
"""
        sections = self.crawler.parse_section_data(course=None, section_data=sample_section_source)
        print sections
        assert sections
        assert len(sections) == 8
        assert sections[0]['section'] == '0101'
        assert sections[0]['teacher'] == 'D. Jacobs'
        
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
        'title': 'Object-Oriented Programming I',
        'permreq': '(PermReq)',
        'details' : None,
        'credits': '4',
        'grade_method': 'REG',
        'requirements': 'Corequisite: MATH140 and permission of department. Not open to students who have completed CMSC114.',
        'description': 'Introduction to programming and computer science. Emphasizes understanding and implementation of applications using object-oriented techniques. Develops skills such as program design and testing as well as implementation of programs using a graphical IDE. Programming done in Java.',
        }
        
        for c in courses:
            if c['code'] == correct_course['code']:
                found = True
                assert len(correct_course) == len(c)
                for k, v in correct_course.items():
                    assert c[k] == v, 'Course check failed!\nGenerated:\t%s\nCorrect:\t%s' % (c[k], v)
            assert len(courses) == 53, 'Found length %d != 53' % len(courses)
        assert found
    
    def test_get_all_courses(self):
        courses = self.crawler.get_all_courses()
        logger.debug(courses)
        
if __name__ == "__main__":
    unittest.main()
    