#!/usr/bin/env python
# -*- coding: utf-8 -*-


class NoFilter(object):
    def __init__(self):
        pass

    def filter(self, translations):
        return translations[:]

    def link(self, next_filter):
        self.next_filter = next_filter
        return self


class CountFilter(NoFilter):
    def __init__(self, max_translations):
        self.next_filter = NoFilter()
        if max_translations < 0:
            raise ValueError(u'Maksymalna liczba tłumaczeń musi być nieujemna')
        self.max_translations = max_translations

    def filter(self, translations):
        filtered = translations[-self.max_translations:]
        return self.next_filter.filter(filtered)


class GroupFilter(NoFilter):
    def __init__(self, groups):
        self.next_filter = NoFilter()
        if groups is None:
            raise ValueError(u'Niezdefiniowane grupy')
        self.groups = groups

    def filter(self, translations):
        filtered = [translation for translation in translations if translation[u'group'] in self.groups]
        return self.next_filter.filter(filtered)
