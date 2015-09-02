# coding=utf-8

SYMBOLS = '+ - * / % === !== == != < > <= >= && || ! = |'.split(' ')
OPERATORS = {x: True for x in SYMBOLS}
ESCAPE = {"n": "\n", "f": "\f", "r": "\r", "t": "\t", "v": "\v", "'": "'", '"': '"'}


class Lexer(object):
    """
    |ref| https://github.com/angular/angular.js/blob/master/src/ng/parse.js
    """

    def __init__(self, text):
        super(Lexer, self).__init__()
        self.text = text
        self.index = 0
        self.tokens = []
        self.filters = []
        self.currentFilter = None

    def lex(self):
        while self.index < len(self.text):
            ch = self.text[self.index]
            if ch == '"' or ch == "'":
                self.readString(ch)
            elif self.isNumber(ch) or (ch == '.' and self.isNumber(self.peek())):
                self.readNumber()
            elif self.isIdent(ch):
                self.readIdent()
            elif self.exists(ch, '(){}[].,;:?'):
                self.tokens.append({'index': self.index, 'text': ch})
                self.index += 1
            elif self.isWhitespace(ch):
                self.index += 1
            else:
                ch2 = ch + self.peek()
                ch3 = ch + self.peek(2)
                op1 = op2 = op3 = None
                try:
                    op1 = OPERATORS[ch]
                except Exception, e:
                    pass
                try:
                    op2 = OPERATORS[ch2]
                except Exception, e:
                    pass
                try:
                    op3 = OPERATORS[ch3]
                except Exception, e:
                    pass
                if op1 or op2 or op3:
                    token = None
                    if op3:
                        token = ch3
                    elif op2:
                        token = ch2
                    else:
                        token = ch
                    self.tokens.append({'index': self.index, 'text': token, 'operator': True})
                    self.index += len(token)
                else:
                    msg = 'Unexpected next character %s %s' % self.index, self.index + 1
                    raise Exception(msg)
        return self.tokens

    def exists(self, ch, chars):
        return chars.find(ch) != -1

    def peek(self, i=None):
        num = i if i else 1
        return self.text[self.index + num] if self.index + num < len(self.text) else False

    def isNumber(self, ch):
        num = None
        try:
            num = int(ch)
            if num >= 0 and num <= 9:
                if isinstance(ch, str) or isinstance(ch, unicode):
                    return True
        except Exception, e:
            pass
        return False

    def isWhitespace(self, ch):
        return ch == ' ' or ch == '\r' or ch == '\t' or ch == '\n' \
               or ch == '\v' or ch == '\u00A0'

    def isIdent(self, ch):
        return 'a' <= ch and ch <= 'z' or \
               'A' <= ch and ch <= 'Z' or \
               '_' == ch or ch == '$'

    def isExpOperator(self, ch):
        return ch == '-' or ch == '+' or self.isNumber(ch)

    def readNumber(self):
        number = ''
        start = self.index
        while self.index < len(self.text):
            ch = self.text[self.index].lower()
            if ch == '.' or self.isNumber(ch):
                number += ch
            else:
                peekch = self.peek()
                if ch == 'e' and self.isExpOperator(peekch):
                    number += ch
                elif self.isExpOperator(ch) and peekch and self.isNumber(peekch) and number[-1] == 'e':
                    number += ch
                elif self.isExpOperator(ch) and (not peekch or not self.isNumber(peekch)) and number[-1] == 'e':
                    raise Exception('Invalid exponent')
                else:
                    break
            self.index += 1
        value = None
        try:
            value = int(number)
        except Exception, e:
            try:
                value = float(number)
            except Exception, e:
                pass

        self.tokens.append({'index': start, 'text': number, 'constant': True, 'value': value})

    def readIdent(self):
        start = self.index
        while self.index < len(self.text):
            ch = self.text[self.index]
            if not self.isIdent(ch) or self.isNumber(ch):
                break
            self.index += 1

        self.tokens.append({'index': start, 'text': self.text[start:self.index], 'identifier': True})

    def readString(self, quote):
        start = self.index
        self.index += 1
        string = ''
        rawString = quote
        escape = False
        while self.index < len(self.text):
            ch = self.text[self.index]
            rawString += ch
            if escape:
                if ch == 'u':
                    hexValue = self.text[self.index + 1]
                    self.index += 1
                    string += hexValue
                else:
                    try:
                        rep = ESCAPE[ch]
                        string += rep
                    except Exception, e:
                        string += ch
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                self.index += 1
                self.tokens.append({'index': start,
                                    'text': rawString,
                                    'constant': True,
                                    'value': string})
                break
            else:
                string += ch
            self.index += 1

    def parseRules(self):
        rules = self.lex()
        if len(rules) > 0:
            for rule in rules:
                self._parseRule(rule)
        return self.filters

    def _parseRule(self, rule):
        identifier = constant = text = value = None
        try:
            identifier = rule['identifier']
            self.currentFilter = {}
            self.currentFilter['name'] = rule['text']
            self.currentFilter['params'] = []
            self.filters.append(self.currentFilter)
        except Exception, e:
            pass

        try:
            constant = rule['constant']
            text = rule['text']
            value = rule['value']
        except Exception, e:
            pass

        if constant:
            param = {'text': text, 'value': value}
            if self.currentFilter and param:
                self.currentFilter['params'].append(param)
