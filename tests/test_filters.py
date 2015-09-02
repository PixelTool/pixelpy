# coding=utf-8
import unittest
from pixel.filters import *

class FilterTest(unittest.TestCase):

    def test_isStr(self):
        str1 = 'str1'
        str2 = '字符'
        str3 = u'字符'
        str4 = [0]
        rst1 = isStr(str1)
        rst2 = isStr(str2)
        rst3 = isStr(str3)
        rst4 = isStr(str4)
        self.assertTrue(rst1)
        self.assertTrue(rst2)
        self.assertTrue(rst3)
        self.assertFalse(rst4)

    def test_dateFilter(self):
        date1 = "12/5/2011"
        fmt1 = [{"value": "YYYY/MM/DD"}]
        date2 = "2012-5-13 10:05:06 pm"
        fmt2 = [{"value": "YYYY/MM/DD HH:mm:ss"}]
        rst = dateFilter(date1, fmt1)
        rst2 = dateFilter(date2, fmt2)
        self.assertEqual(rst, '2011/12/05')
        self.assertEqual(rst2, '2012/05/13 22:05:06')

    def test_substrFilter(self):
        value = "hello world"
        params = [{"value": 1}, {"value": 3}]
        value2 = "helloworld"
        params2 = [{"value": 2}]
        rst = substrFilter(value, params)
        rst2 = substrFilter(value2, params2)
        self.assertEqual(rst, 'ell')
        self.assertEqual(rst2, 'lloworld')

    def test_substringFilter(self):
        value = "hello world"
        params = [{"value": 1}, {"value": 3}]
        value2 = "helloworld"
        params2 = [{"value": 2}]
        rst = substringFilter(value, params)
        rst2 = substringFilter(value2, params2)
        self.assertEqual(rst, 'el')
        self.assertEqual(rst2, 'lloworld')

    def test_splitFilter(self):
        value = '1,2,3,4,5'
        params = [{"value": ","}, {"value": 3}]
        rst = splitFilter(value, params)
        self.assertEqual(rst, ['1', '2', '3', '4,5'])

    def test_replaceFilter(self):
        value = 'nihao, world!'
        pattern = "\w{5},"
        params = [{"value": pattern}, {"value": "hello"}]
        rst = replaceFilter(value, params)
        self.assertEqual(rst, 'hello world!')

    def test_matchFilter(self):
        value = 'nihao, world!'
        pattern = "\w{5},"
        params = [{"value": pattern}]
        rst = matchFilter(value, params)
        self.assertEqual(rst, 'nihao,')

    def test_Filter(self):
        rule = 'lowercase|uppercase|replace:"\\\\d":"a"|match:"\\\\w"'
        value = 'hahahUIO123'

        filt = Filter(value, rule)
        self.assertEqual(filt.result(), 'H')

        rule1 = 'date|"YYYY|MM月DD"'
        value1 = '2010/10/20'
        filt.value = value1
        filt.setfilter_text(rule1)
        self.assertEqual(filt.result(), '2010|10月20')

        rule2 = 'uppercase|replace:"\\\\d":"a"'
        value2 = 'hello123'
        filt.value = value2
        filt.setfilter_text(rule2)
        self.assertEqual(filt.result(), 'HELLOaaa')