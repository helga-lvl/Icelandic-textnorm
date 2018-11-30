#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import inspect


class SemioticClasses:

    def __init__(self, label):
        self.available_classes = [name for name in inspect.getmembers(sys.modules[__name__])]
        self.semiotic_class = self.find_class_for(label)

    def find_class_for(self, label):
        for cl in self.available_classes:
           if cl[0].lower() == label:
               return cl[1]()


class SemioticClass:

    DIV = '|'
    INT_ATTR = 'integer:'

    def __init__(self, name, preserve_ord=False):
        self.name = name
        self.preserve_ord = preserve_ord

    def set_attribute(self, attr_value):
        if not self.valid_tuple(attr_value):
            raise ValueError

    def serialize_to_string(self):
        raise NotImplementedError

    def grammar_attributes(self):
        raise NotImplementedError

    def valid_tuple(self, tup):
        if tup and len(tup) == 2:
            return True
        return False

    def invalid_attribute(self, attr):
        raise ValueError


class Cardinal(SemioticClass):

    def __init__(self, preserve_ord=False):
        super().__init__('cardinal', preserve_ord)
        self.integer = None

    def __str__(self):
        return 'Cardinal integer: ' + self.integer

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.INT_ATTR:
            self.integer = attr_value[1]
        else:
            super().invalid_attribute(attr_value)

    def attribute_is_set(self, attr):
        if attr == self.INT_ATTR and self.integer:
            return True
        return False

    def serialize_to_string(self):
        return '{}{}{} {} {}'.format(self.name, self.DIV, self.INT_ATTR, self.integer, self.DIV)

    def grammar_attributes(self):
        return [(self.INT_ATTR, self.integer)]


class Ordinal(SemioticClass):

    def __init__(self, preserve_ord=False):
        super().__init__('ordinal', preserve_ord)
        self.integer = None

    def __str__(self):
        return 'Ordinal integer: ' + self.integer

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.INT_ATTR:
            self.integer = attr_value[1]
        else:
            super().invalid_attribute(attr_value)

    def attribute_is_set(self, attr):
        if attr == self.INT_ATTR and self.integer:
            return True
        return False

    def serialize_to_string(self):
        return '{}{}{} {} {}'.format(self.name, self.DIV, self.INT_ATTR, self.integer, self.DIV)

    def grammar_attributes(self):
        return [(self.INT_ATTR, self.integer)]


class Decimal(SemioticClass):

    INT_PART = 'integer_part:'
    FRACT_PART = 'fractional_part:'

    def __init__(self, preserve_ord=False):
        super().__init__('decimal', preserve_ord)
        self.integer_part = None
        self.fractional_part = None
        self.preserve_ord = preserve_ord

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.INT_PART:
            self.set_integer_part(attr_value[1])
        elif attr_value[0] == self.FRACT_PART:
            self.set_fractional_part(attr_value[1])
        else:
            super().invalid_attribute(attr_value)

    def set_integer_part(self, val):
        self.integer_part = val

    def set_fractional_part(self, val):
        self.fractional_part = val

    def __str__(self):
        return 'Decimal: ' + str(self.grammar_attributes())

    def attribute_is_set(self, attr):
        if attr == self.INT_PART and self.integer_part:
            return True
        if attr == self.FRACT_PART and self.fractional_part:
            return True
        return False

    def serialize_to_string(self):
        return '{}{}{} {} {} {} {} {}'.format(
            self.name, self.DIV, self.INT_PART, self.integer_part, self.DIV, self.FRACT_PART, self.fractional_part, self.DIV)

    def grammar_attributes(self):
        return [(self.INT_PART, self.integer_part), (self.FRACT_PART, self.fractional_part)]


class Time(SemioticClass):

    HOURS = 'hours:'
    MINUTES = 'minutes:'

    def __init__(self, preserve_ord=False):
        super().__init__('time', preserve_ord)
        self.hours = None
        self.minutes = None

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.HOURS:
            self.set_hours(attr_value[1])
        elif attr_value[0] == self.MINUTES:
            self.set_minutes(attr_value[1])
        else:
            super().invalid_attribute(attr_value)

    def set_hours(self, val):
        self.hours = val

    def set_minutes(self, val):
        self.minutes = val

    def __str__(self):
        return 'Time: ' + str(self.grammar_attributes())

    def attribute_is_set(self, attr):
        if attr == self.HOURS and self.hours:
            return True
        if attr == self.MINUTES and self.minutes:
            return True
        return False

    def serialize_to_string(self):
        return '{}{}{} {} {} {} {} {}'.format(
            self.name, self.DIV, self.HOURS, self.hours, self.DIV, self.MINUTES, self.minutes, self.DIV)

    def grammar_attributes(self):
        return [(self.HOURS, self.hours), (self.MINUTES, self.minutes)]


class Date(SemioticClass):

    DAY = 'day:'
    MONTH = 'month:'
    YEAR = 'year:'

    def __init__(self, preserve_ord=False):
        super().__init__('date', preserve_ord)
        self.day = None
        self.month = None
        self.year = None

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.DAY:
            self.set_day(attr_value[1])
        elif attr_value[0] == self.MONTH:
            self.set_month(attr_value[1])
        elif attr_value[0] == self.YEAR:
            self.set_year(attr_value[1])
        else:
            super().invalid_attribute(attr_value)

    def set_day(self, val):
        self.day = val

    def set_month(self, val):
        self.month = val

    def set_year(self, val):
        self.year = val

    def __str__(self):
        return 'Date: ' + str(self.grammar_attributes())

    def attribute_is_set(self, attr):
        if attr == self.DAY and self.day:
            return True
        if attr == self.MONTH and self.month:
            return True
        if attr == self.YEAR and self.year:
            return True

        return False

    def serialize_to_string(self):
        if self.year:
            return '{}{}{} {} {} {} {} {} {} {} {}'.format(
                self.name, self.DIV, self.DAY, self.day, self.DIV, self.MONTH, self.month, self.DIV, self.YEAR, self.year, self.DIV)
        else:
            return '{}{}{} {} {} {} {} {}'.format(
                self.name, self.DIV, self.DAY, self.day, self.DIV, self.MONTH, self.month, self.DIV)

    def grammar_attributes(self):
        if self.year:
            return [(self.DAY, self.day), (self.MONTH, self.month), (self.YEAR, self.year)]
        else:
            return [(self.DAY, self.day), (self.MONTH, self.month)]


class Connector(SemioticClass):

    VALID_LABELS = ['cardinal', 'ordinal', 'decimal', 'date', 'time']
    CONN = 'connector:'

    def __init__(self, preserve_ord=False):
        super().__init__('connector', preserve_ord)
        self.from_val = None
        self.to_val = None
        self.connector = None

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if label in self.VALID_LABELS:
            sem_class = SemioticClasses(label).semiotic_class
            if not self.from_val:
                self.set_from_value(sem_class)
                self.from_val.set_attribute(attr_value)
            elif not self.from_val.attribute_is_set(attr_value[0]):
                self.from_val.set_attribute(attr_value)
            elif isinstance(sem_class, type(self.from_val)) and not self.to_val:
                self.set_to_value(sem_class)
                self.to_val.set_attribute(attr_value)
            elif self.to_val:
                self.to_val.set_attribute(attr_value)
            else:
                raise ValueError
        elif attr_value[0] == self.CONN:
            self.set_connector(attr_value[1])
        else:
            raise ValueError

    def set_from_value(self, val):
        self.from_val = val

    def set_to_value(self, val):
        self.to_val = val

    def set_connector(self, conn):
        self.connector = conn

    def __str__(self):
        return 'Connector: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        return '{}{}{} {} {} {} {}'.format(
            self.name, self.DIV, self.from_val.serialize_to_string(), self.CONN, self.connector, self.DIV, self.to_val.serialize_to_string())

    def grammar_attributes(self):
        return [(self.from_val.name, self.from_val), (self.CONN, self.connector), (self.to_val.name, self.to_val)]


class Acronym(SemioticClass):

    HEAD = 'head:'
    TAIL = 'tail:'

    def __init__(self, preserve_ord=False):
        super().__init__('acronym', preserve_ord)
        self.head = None
        self.tail = None

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.HEAD:
            self.set_head(attr_value[1])
        elif attr_value[0] == self.TAIL:
            self.set_tail(attr_value[1])
        else:
            super().invalid_attribute(attr_value)

    def set_head(self, val):
        self.head = val

    def set_tail(self, val):
        self.tail = val

    def __str__(self):
        return 'Acronym: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        if self.tail:
            return '{}{}{} {} {} {} {} {}'.format(
                self.name, self.DIV, self.HEAD, self.head, self.DIV, self.TAIL, self.tail, self.DIV)
        else:
            return '{}{}{} {} {}'.format(self.name, self.DIV, self.HEAD, self.head, self.DIV)

    def grammar_attributes(self):
        return [(self.HEAD, self.head), (self.TAIL, self.tail)]


class Abbreviation(SemioticClass):

    ABBR = 'abbr:'

    def __init__(self, preserve_ord=False):
        super().__init__('abbreviation', preserve_ord)
        self.abbr = None

    def __str__(self):
        return 'Abbreviation: ' + str(self.grammar_attributes())

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if attr_value[0] == self.ABBR:
            self.set_abbreviation(attr_value[1])
        else:
            super().invalid_attribute(attr_value)

    def set_abbreviation(self, val):
        self.abbr = val

    def serialize_to_string(self):
        return '{}{}{} {} {}'.format(self.name, self.DIV, self.ABBR, self.abbr, self.DIV)

    def grammar_attributes(self):
        return [(self.ABBR, self.abbr)]


class Percent(SemioticClass):
    #TODO: needs cardinal as well

    DEC_LABEL = 'decimal'
    SYMBOL = 'symbol:'

    def __init__(self, preserve_ord=False):
        super().__init__('percent', preserve_ord)
        self.decimal = None
        self.symbol = None

    def __str__(self):
        return 'Percent: ' + str(self.grammar_attributes())

    def set_attribute(self, attr_value, label=''):
        super().set_attribute(attr_value)
        if label == self.DEC_LABEL:
            sem_class = SemioticClasses(label).semiotic_class
            if not self.decimal:
                self.set_decimal(sem_class)
            self.decimal.set_attribute(attr_value)

        elif attr_value[0] == self.SYMBOL:
            self.set_symbol(attr_value[1])
        else:
            super().invalid_attribute(attr_value)

    def set_decimal(self, val):
        self.decimal = val

    def set_symbol(self, sym):
        self.symbol = sym

    def serialize_to_string(self):
        return '{}{}{} {} {} {}'.format(
            self.name, self.DIV, self.decimal.serialize_to_string(), self.SYMBOL, self.symbol, self.DIV)

    def grammar_attributes(self):
        return [(self.DEC_LABEL, self.decimal), (self.SYMBOL, self.symbol)]


def main():
    sem = SemioticClasses('cardinal')

    #dec = Decimal(('10', '5'))
    #for elem in sem.available_classes:
    #    if inspect.isclass(elem[1]):
    #        if isinstance(dec, elem[1]):
    #            print('Found class: ' + str(elem))
    #            for attr in dec.grammar_attributes():
    #                print('Grammar attr: ' + str(attr))

if __name__ == '__main__':
    main()