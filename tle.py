'''
Created on Nov 26, 2015

@author: trice
'''
import unittest
import requests
from dateutil.parser import parse
import datetime

class tle():
    
    def __init__(self, 
                 url='http://www.celestrak.com/NORAD/elements/visual.txt',
                 refetchseconds = 7200):
        self.url = url
        self.last_modified = None
        self.data = dict()
        self.r = None
        
    def fetch(self, recurse=True):
        self.r = requests.get(self.url)
        self.last_modified = parse(self.r.headers['Last-Modified']).replace(tzinfo=None)
        self.age_in_sec = (datetime.datetime.utcnow() - self.last_modified).total_seconds()
        if self.age_in_sec > 172800 and recurse:
            self.r.clear_cache()
            self.fetch(recurse=False)
        
    def parse(self):
        lines = ''.join(str(self.r.text)).rstrip().split('\n')
        for line1, line2, line3 in zip(*[iter(lines)] * 3):
            line1 = line1.rstrip()
            self.data[line1] = [line1, line2, line3]



class Test(unittest.TestCase):
    import requests_cache
    requests_cache.install_cache('tle_test_webcache', backend='sqlite', expire_after=3600)

    def test_cache_enabled_in_testing(self):
        mytle = tle()
        mytle.fetch()
        self.assertTrue(mytle.r.from_cache)

    def test_fresh_data(self):
        mytle = tle()
        mytle.fetch()
        age_in_sec = datetime.datetime.utcnow() - mytle.last_modified
        self.assertLess(age_in_sec.total_seconds(), 604800) # 1 week in seconds

    def test_sats(self):
        mytle = tle()
        mytle.fetch()
        mytle.parse()
        self.assertTrue('ISS (ZARYA)' in mytle.data.keys()) 
        self.assertTrue('HST' in mytle.data.keys()) 
        self.assertGreaterEqual(len(mytle.data.keys()), 70) 
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()