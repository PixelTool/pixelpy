# coding=utf-8
import logging
from .filters import Filter

logging.basicConfig(
    format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
    level=logging.CRITICAL
)


def parse(selector, rule, ps=None):
    if not rule:
        return None

    rst = {}
    r_name = rule.get('name')
    r_type = rule.get('type')
    r_def = rule.get('def')
    r_source = rule.get('source')
    r_selector = None
    if r_source:
        r_selector = r_source.get('selector')

    if r_name == u'[root]':
        if r_type == u'{}':
            rst = result_for_rule_type_dict(selector, r_selector, r_def)
        elif r_type == u'[]':
            rst = result_for_rule_type_array(selector, r_selector, r_def)
    else:
        rst['name'] = r_name
        if r_type == u'string':
            if r_source:
                r = result_for_rule_type_string(selector, r_source, ps)
                rst['value'] = r
                if isinstance(r, list):
                    rst['len'] = len(r)
            else:
                rst['value'] = None

        elif r_type == u'{}':
            r = result_for_rule_type_dict(selector, r_selector, r_def)
            rst['value'] = r

        elif r_type == u'[]':
            r = result_for_rule_type_array(selector, r_selector, r_def)
            rst['value'] = r
    logging.debug('>>> %s %s %s', r_name, r_selector, rst)
    return rst if rst and len(rst) > 0 else None


def result_for_rule_type_dict(selector, r_selector, r_def):
    result = {}
    for i in r_def:
        r = None
        if r_selector:
            try:
                s_selector = i['source']['selector']
                result = parent_and_child(r_selector, s_selector)
                i['source']['selector'] = result['sub']
                r = parse(selector, i, result['ps'])
            except Exception, e:
                print e
        else:
            r = parse(selector, i)
        try:
            if r and r['name'] and r['value']:
                result[r['name']] = r['value']
        except Exception, e:
            pass
    return result


def result_for_rule_type_array(selector, r_selector, r_def):
    result = []
    if r_selector:
        parent = None
        for i in r_def:
            try:
                s_selector = i['source']['selector']
                ret = parent_and_child(r_selector, s_selector)
                parent = ret['ps']
                if parent:
                    i['source']['selector'] = ret['sub']
            except Exception, e:
                pass

        if parent:
            items = selector.css(parent)
            for item in items:
                tempValue = {}
                for i in r_def:
                    r = parse(item, i)
                    try:
                        if r and r['name'] and r['value']:
                            tempValue[r['name']] = r['value']
                    except Exception, e:
                        raise e
                if tempValue and len(tempValue):
                    result.append(tempValue)

        else:
            result = result_for_array_without_parent_selector(selector, r_def)
    else:
        result = result_for_array_without_parent_selector(selector, r_def)
    return result


def result_for_array_without_parent_selector(selector, r_def):
    result = []
    temp_rst = []
    logging.debug('>>> %s', r_def)
    for i in r_def:
        r = parse(selector, i, '[]')
        logging.debug(r)
        try:
            if r and r['name'] and r['value']:
                temp_rst.append(r)
        except Exception, e:
            pass
    maxLen = 0
    for i in temp_rst:
        try:
            length = i['len']
            maxLen = length if length > maxLen else maxLen
        except Exception, e:
            pass
    for i in xrange(0, maxLen):
        r = {}
        for j in temp_rst:
            try:
                item = j['value']
                val = item[i]
                if val:
                    r[j['name']] = val

            except Exception, e:
                pass
        if len(r):
            result.append(r)
    return result


def result_for_rule_type_string(selector, source, ps=None):

    if not source:
        return None

    result = None
    method = source.get('method')
    r_selector = source.get('selector')
    r_filter = source.get('filter')
    if not ps:
        result = ''.join(result_with_method(selector, r_selector, method))
        if r_filter:
            filt = Filter(result, r_filter)
            result = filt.result().strip()

    elif ps == '[]':
        """
        |ref| result_for_array_without_parent_selector
        """
        result = result_with_method(selector, r_selector, method)

        if r_filter:
            filt = Filter(None, r_filter)
            temp = []
            for i in result:
                filt.value = i
                r = filt.result()
                logging.info(']]] %s', r)
                if r and r.strip():
                    temp.append(r.strip())
            result = temp
    else:
        temp = selector.css(ps)
        if len(temp) > 0:
            selector = temp[0]
            result = ''.join(result_with_method(selector, r_selector, method))
            if r_filter:
                filt = Filter(result, r_filter)
                result = filt.result().strip()
    return result


def result_with_method(selector, r_selector, method):
    result = None
    if method == u'text':
        result = selector.css(r_selector + '::text').extract()
    elif method == u'html':
        result = selector.css(r_selector).extract()
    elif method.find(u'[') != -1:
        attr = method.lstrip('[').rstrip(']')
        result = selector.css(r_selector + '::attr(' + attr + ')').extract()
    return result


def parent_and_child(parent, child):
    arrp = parent.split('>')
    p_length = len(arrp)
    arrc = child.split('>')
    ps = '>'.join(arrp).strip()
    sub = '>'.join(arrc[p_length:]).strip()
    return {'ps': ps, 'sub': sub}
