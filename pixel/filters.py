# coding=utf-8
import re
import json
import arrow
from dateutil.parser import parse
from dateparser.date import DateDataParser
from .lexer import Lexer


def isStr(value):
    return isinstance(value, str) or isinstance(value, unicode)


def lowercaseFilter(value, params=None):
    return value.lower() if isStr(value) else value


def uppercaseFilter(value, params=None):
    return value.upper() if isStr(value) else value


def dateFilter(value, params=None):
    if not value or not value.strip():
        return value
    fmt = None
    try:
        fmt = params[0]['value']
    except Exception, e:
        pass

    if fmt:
        try:
            d = parse(value)
            value = arrow.get(d, 'Asia/Shanghai').format(fmt)
        except Exception, e:
            try:
                value = arrow.get(value, 'Asia/Shanghai').format(fmt)
            except Exception, e:
                try:
                    ddp = DateDataParser()
                    ret = ddp.get_date_data(value)
                    dateobj = ret['date_obj']
                    ts = arrow.get(dateobj).timestamp + 8 * 60 * 60
                    value = arrow.get(ts).format(fmt)
                except Exception, e:
                    pass

    return value


def substrFilter(value, params=None):
    p = p1 = None
    try:
        p = params[0]['value']
        p1 = params[1]['value']
    except Exception, e:
        pass

    if p and not p1:
        return value[p:] if isStr(value) else value
    elif p and p1:
        return value[p:p + p1] if isStr(value) else value
    else:
        return value


def substringFilter(value, params=None):
    p = p1 = None
    try:
        p = params[0]['value']
        p1 = params[1]['value']
    except Exception, e:
        pass

    if p and not p1:
        return value[p:] if isStr(value) else value
    elif p and p1:
        return value[p:p1] if isStr(value) else value
    else:
        return value


def jsonFilter(value, params=None):
    if value:
        return json.dumps(value)
    return value


def splitFilter(value, params=None):
    delimiter = limit = None
    try:
        delimiter = params[0]['value']
        limit = params[1]['value']
    except Exception, e:
        pass

    if delimiter:
        return value.split(delimiter, limit) if isStr(value) else value
    return value


def replaceFilter(value, params=None):
    pattern = repl = None
    try:
        pattern = params[0]['value']
        repl = params[1]['value']
    except Exception, e:
        pass
    if pattern:
        regexp = re.compile(pattern)
        repl = repl if repl else ''
        return re.sub(regexp, repl, value) if isStr(value) else value
    return value


def matchFilter(value, params=None):
    pattern = None
    try:
        pattern = params[0]['value']
    except Exception, e:
        pass

    if pattern:
        regexp = re.compile(pattern)
        if isStr(value):
            match = regexp.match(value)
            if match:
                return match.group(0)
    return value


filters = {'lowercase': lowercaseFilter,
           'uppercase': uppercaseFilter,
           'date': dateFilter,
           'substr': substrFilter,
           'substring': substringFilter,
           'json': jsonFilter,
           'split': splitFilter,
           'replace': replaceFilter,
           'match': matchFilter}


class Filter(object):

    def __init__(self, value, filter_text):
        self.value = value
        self.filterText = filter_text
        self.rules = Lexer(self.filterText).parseRules()

    def setfilter_text(self, filter_text):
        self.filterText = filter_text
        self.rules = Lexer(self.filterText).parseRules()

    def result(self):
        for rule in self.rules:
            self.apply_filter(rule)
        return self.value

    def apply_filter(self, rule):
        for key in filters:
            name = rule.get('name', None)
            if key == name:
                params = rule.get('params', [])
                self.value = filters[key](self.value, params)


if __name__ == '__main__':
    rule = 'lowercase|uppercase|replace:"\\\\d":"a"|match:"\\\\w"'

    value = 'hahahUIO123'

    filt = Filter(value, rule)
    print filt.result()

    rule1 = 'date|"YYYY|MM月DD"'
    value1 = '2010/10/20'
    filt.value = value1
    filt.setfilter_text(rule1)
    print filt.result()
