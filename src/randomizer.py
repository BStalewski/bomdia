#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

random.seed()


class SimpleRandomizer(object):
    def __init__(self, first, last):
        random.seed()
        self.first = first
        self.last = last

    def next_random(self):
        return random.randint(self.first, self.last)


class AvoidRepeatRandomizer(SimpleRandomizer):
    def __init__(self, first, last, *args, **kwargs):
        super(AvoidRepeatRandomizer, self).__init__(first, last, *args, **kwargs)
        self.reset_free_numbers()

    def next_random(self):
        if len(self.free_numbers) == 0:
            self.reset_free_numbers()

        index = random.randint(0, len(self.free_numbers) - 1)
        random_number = self.free_numbers[index]
        self.free_numbers[index] = self.free_numbers[-1]
        self.free_numbers.pop()

        return random_number

    def reset_free_numbers(self):
        self.free_numbers = range(self.first, self.last + 1)
