#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from repeat_pl_br import (AvoidRepeatRandomizer, SimpleRandomizer, WordsDict, WordsTestEngine,
                          CountFilter, GroupFilter)


class WordsDictTests(unittest.TestCase):
    def setUp(self):
        self.nonempty_lines = [
            'kobieta;a mulher;woman;basics\n',
            'chłopiec;o menino;boy;basics2',
        ]
        self.expected_entries = [
            {
                'pl': 'kobieta',
                'br': 'a mulher',
                'en': 'woman',
                'group': 'basics',
            },
            {
                'pl': 'chłopiec',
                'br': 'o menino',
                'en': 'boy',
                'group': 'basics2',
            },
        ]
        self.empty_dict = WordsDict.from_string_io([])
        self.nonempty_dict = WordsDict.from_string_io(self.nonempty_lines)
        self.nonempty_dict_cut = WordsDict.from_string_io(self.nonempty_lines).apply_filter(CountFilter(1))
        self.nonempty_dict_bigcut = WordsDict.from_string_io(self.nonempty_lines).apply_filter(CountFilter(3))
        self.reset_dict = WordsDict.from_string_io(self.nonempty_lines).apply_filter(CountFilter(1))

    def test_empty_file_len(self):
        self.assertEqual(len(self.empty_dict), 0)

    def test_nonempty_file_len(self):
        self.assertEqual(len(self.nonempty_dict), 2)

    def test_dict_cut_file_len(self):
        self.assertEqual(len(self.nonempty_dict_cut), 1)
        self.assertEqual(len(self.nonempty_dict_bigcut), 2)

    def test_groups(self):
        expected_groups = {'basics', 'basics2'}
        self.assertEqual(self.nonempty_dict.get_groups(), expected_groups)

    def test_get(self):
        self.assertEqual(self.nonempty_dict[0], self.expected_entries[0])

        with self.assertRaises(IndexError):
            self.nonempty_dict[len(self.nonempty_lines)]

    def test_clear_filter(self):
        self.assertEqual(len(self.reset_dict), 1)
        self.reset_dict.clear_filter()
        self.assertEqual(self.reset_dict[0], self.expected_entries[0])
        self.assertEqual(self.reset_dict[1], self.expected_entries[1])


class WordsTestEngineTests(unittest.TestCase):
    def setUp(self):
        self.multi_lines = [
            'cześć;oi|olá;hi|hello;basics',
            'dzień;o dia;day;basics',
        ]
        self.multi_dict = WordsDict.from_string_io(self.multi_lines)
        self.test_engine = WordsTestEngine(self.multi_dict, pl_to_br=True)

    def test_get_dict_entry(self):
        expected_dict_entry = {
            'pl': 'cześć',
            'br': 'oi|olá',
            'en': 'hi|hello',
            'group': 'basics',
        }
        self.assertEqual(self.test_engine.get_dict_entry(0), expected_dict_entry)

    def test_get_expected_answers(self):
        expected_answers = ['oi', 'olá']
        dict_entry = self.test_engine.get_dict_entry(0)
        self.assertEqual(self.test_engine.get_expected_answers(dict_entry), expected_answers)

    def test_no_error(self):
        dict_entry = self.test_engine.get_dict_entry(1)
        error = self.test_engine.get_error(dict_entry, 'o dia')
        self.assertIsNone(error)

    def test_single_error(self):
        dict_entry = self.test_engine.get_dict_entry(1)
        answer = 'dia'
        expected_error = {
            'expected': ['o dia', ],
            'answer': answer,
            'question': 'dzień',
        }
        self.assertEqual(self.test_engine.get_error(dict_entry, answer), expected_error)

    def test_multi_ok(self):
        dict_entry = self.test_engine.get_dict_entry(0)
        error_oi = self.test_engine.get_error(dict_entry, 'oi')
        error_ola = self.test_engine.get_error(dict_entry, 'olá')
        self.assertIsNone(error_oi)
        self.assertIsNone(error_ola)

    def test_multi_error(self):
        dict_entry = self.test_engine.get_dict_entry(0)
        answer = 'tchau'
        expected_error = {
            'expected': ['oi', 'olá', ],
            'answer': answer,
            'question': 'cześć',
        }
        self.assertEqual(self.test_engine.get_error(dict_entry, answer), expected_error)

    def test_precision(self):
        dict_entry = self.test_engine.get_dict_entry(0)
        answer = 'ola'
        expected_error = {
            'expected': ['oi', 'olá', ],
            'answer': answer,
            'question': 'cześć',
        }
        self.assertEqual(self.test_engine.get_error(dict_entry, answer), expected_error)


class SimpleRandomizerTests(unittest.TestCase):
    def setUp(self):
        self.first = 0
        self.last = 10
        self.simple_randomizer = SimpleRandomizer(self.first, self.last)

    def test_range(self):
        for _ in range(100):
            number = self.simple_randomizer.next_random()
            self.assertTrue(self.first <= number <= self.last)


class AvoidRepeatRandomizerTests(unittest.TestCase):
    def setUp(self):
        self.first = 0
        self.last = 10
        self.avoid_randomizer = AvoidRepeatRandomizer(self.first, self.last)

    def test_range(self):
        numbers_count = 2 * (self.last - self.first + 1)
        for _ in range(numbers_count):
            number = self.avoid_randomizer.next_random()
            self.assertTrue(self.first <= number <= self.last)

    def test_avoiding(self):
        def fill_set():
            drawn_numbers = set()
            for _ in range(numbers_count):
                number = self.avoid_randomizer.next_random()
                drawn_numbers.add(number)

            return drawn_numbers

        numbers_count = self.last - self.first + 1

        drawn_numbers = fill_set()
        self.assertEqual(len(drawn_numbers), numbers_count)

        drawn_numbers = fill_set()
        self.assertEqual(len(drawn_numbers), numbers_count)


class CountFilterTests(unittest.TestCase):
    def setUp(self):
        self.translations = [
            {
                'pl': 'kobieta',
                'br': 'a mulher',
                'en': 'woman',
                'group': 'basics',
            },
            {
                'pl': 'dziewczyna',
                'br': 'a menina',
                'en': 'girl',
                'group': 'basics',
            },
            {
                'pl': 'mężczyzna',
                'br': 'o homem',
                'en': 'man',
                'group': 'basics2',
            },
            {
                'pl': 'chłopiec',
                'br': 'o menino',
                'en': 'boy',
                'group': 'basics2',
            },
        ]
        self.count_filter = CountFilter(1)
        self.big_count_filter = CountFilter(len(self.translations) + 1)

    def test_small_count(self):
        filtered = self.count_filter.filter(self.translations)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered, self.translations[-1:])

    def test_big_count(self):
        filtered = self.big_count_filter.filter(self.translations)
        self.assertEqual(len(filtered), len(self.translations))
        self.assertEqual(filtered, self.translations)


class GroupFilterTests(unittest.TestCase):
    def setUp(self):
        self.translations = [
            {
                'pl': 'kobieta',
                'br': 'a mulher',
                'en': 'woman',
                'group': 'basics',
            },
            {
                'pl': 'dziewczyna',
                'br': 'a menina',
                'en': 'girl',
                'group': 'basics',
            },
            {
                'pl': 'mężczyzna',
                'br': 'o homem',
                'en': 'man',
                'group': 'basics2',
            },
            {
                'pl': 'chłopiec',
                'br': 'o menino',
                'en': 'boy',
                'group': 'basics2',
            },
        ]
        self.single_group_filter = GroupFilter({'basics'})
        self.unknown_group_filter = GroupFilter({'unknown'})
        self.multi_group_filter = GroupFilter({'basics', 'basics2'})

    def test_single_group(self):
        filtered = self.single_group_filter.filter(self.translations)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered, self.translations[:2])

    def test_unknown_group(self):
        filtered = self.unknown_group_filter.filter(self.translations)
        self.assertEqual(len(filtered), 0)

    def test_multi_groups(self):
        filtered = self.multi_group_filter.filter(self.translations)
        self.assertEqual(len(filtered), len(self.translations))
        self.assertEqual(filtered, self.translations)


class MixedFilterTests(unittest.TestCase):
    def setUp(self):
        self.translations = [
            {
                'pl': 'kobieta',
                'br': 'a mulher',
                'en': 'woman',
                'group': 'basics',
            },
            {
                'pl': 'dziewczyna',
                'br': 'a menina',
                'en': 'girl',
                'group': 'basics',
            },
            {
                'pl': 'mężczyzna',
                'br': 'o homem',
                'en': 'man',
                'group': 'basics2',
            },
            {
                'pl': 'chłopiec',
                'br': 'o menino',
                'en': 'boy',
                'group': 'basics2',
            },
        ]
        self.mixed_filter = GroupFilter({'basics2'}).link(CountFilter(1))

    def test_mixed_filters(self):
        filtered = self.mixed_filter.filter(self.translations)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered, self.translations[-1:])


if __name__ == '__main__':
    unittest.main()
