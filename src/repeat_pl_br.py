#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv

from filters import CountFilter, GroupFilter
from communication import get_test_parameters, choose_repeat_mode, RepeatMode
from randomizer import AvoidRepeatRandomizer, SimpleRandomizer
from utils import get_fake_file, print_error, print_info, print_ok


DICT_FILE = 'pt_br_words.csv'


class WordsDict:
    GROUP_KEY = 'group'

    def __init__(self, csv_reader):
        self.all_translations = []
        try:
            self.header = next(csv_reader)
        except StopIteration:
            raise ValueError('WordsDict - empty file')

        if self.GROUP_KEY not in self.header:
            raise ValueError('WordsDict - incorrect header - missing %s field' % (self.GROUP_KEY,))

        for (i, line) in enumerate(csv_reader, 1):
            if len(self.header) != len(line):
                line_num = csv_reader.line_num
                raise ValueError('WordsDict - wrong fields (%s) number in line %d.' % (line, line_num))

            translation = dict(zip(self.header, line))
            self.all_translations.append(translation)
        self.translations = self.all_translations[:]

    def __len__(self):
        return len(self.translations)

    def __getitem__(self, index):
        return self.translations[index]

    def get_langs(self):
        return [lang for lang in self.header if lang != self.GROUP_KEY]

    def get_groups(self):
        return {translation[self.GROUP_KEY] for translation in self.translations}

    def apply_filter(self, translations_filter):
        self.translations = translations_filter.filter(self.translations)
        return self

    def clear_filter(self):
        self.translations = self.all_translations[:]

    @staticmethod
    def from_string_io(string_io):
        fake_file = get_fake_file(string_io)
        reader = csv.reader(fake_file, delimiter=';')
        words_dict = WordsDict(reader)
        return words_dict


class WordsTestEngine:
    def __init__(self, words_dict, ask_lang, ans_lang, avoid_repeat=True):
        if ask_lang == ans_lang:
            raise ValueError('Język pytania taki sam jak język odpowiedzi %s' % ask_lang)
        self.words_dict = words_dict
        self.ask_lang = ask_lang
        self.ans_lang = ans_lang

        if avoid_repeat:
            self.randomizer = AvoidRepeatRandomizer(0, len(self.words_dict) - 1)
        else:
            self.randomizer = SimpleRandomizer(0, len(self.words_dict) - 1)

    def get_dict_entry(self, index=None):
        index = self.randomizer.next_random() if index is None else index
        return self.words_dict[index]

    def get_expected_answers(self, dict_entry):
        expected_answers_list = dict_entry[self.ans_lang]
        expected_answers = expected_answers_list.split('|')
        lowered_expected_answers = map(str.lower, expected_answers)
        return lowered_expected_answers

    def get_error(self, dict_entry, answer):
        lowered_answer = answer.lower()
        expected_answers = self.get_expected_answers(dict_entry)
        if lowered_answer not in expected_answers:
            question = dict_entry[self.ask_lang]
            return {
                'expected': expected_answers,
                'answer': answer,
                'question': question,
            }
        else:
            return None


class WordsTest:
    def __init__(self, words_dict, tests_num, ask_lang, ans_lang, quick_feedback=True):
        self.tests_engine = WordsTestEngine(words_dict, ask_lang, ans_lang)
        self.tests_num = tests_num
        self.init_status(False)
        self.quick_feedback = quick_feedback

    def test(self, use_cache):
        self.init_status(not use_cache)
        for test_num in range(self.tests_num):
            dict_entry = self.get_dict_entry(test_num, use_cache)
            self.ask_question(dict_entry)
            answer = self.read_answer(dict_entry)
            self.update_status(dict_entry, answer)

        self.present_results()

    def get_dict_entry(self, test_num, use_cache=False):
        if use_cache:
            return self.cache[test_num]
        else:
            dict_entry = self.tests_engine.get_dict_entry()
            self.cache.append(dict_entry)
            return dict_entry

    def ask_question(self, dict_entry):
        question = self.make_question(dict_entry)
        print_info(question)

    def read_answer(self, dict_entry):
        lang = 'brazylijsku' if self.tests_engine.ans_lang == 'br' else 'polsku'
        answer = raw_input('Po %s: ' % lang)
        return answer

    def update_status(self, dict_entry, answer):
        error = self.tests_engine.get_error(dict_entry, answer)
        if error:
            self.wrong_answers.append(error)

        if self.quick_feedback:
            self.present_quick_feedback(error)

    def present_quick_feedback(self, error):
        if error:
            answer = error['answer']
            expected = error['expected']
            expected_options = ' lub '.join(expected)
            print_error('Błąd: "%s" -> "%s"' % (answer, expected_options))
        else:
            print_ok('OK')

    def present_results(self):
        errors_count = len(self.wrong_answers)
        if errors_count == 0:
            print_ok('Doskonale! Bezbłędnie!!!')
        else:
            print_error('Niestety nie było bezbłędnie')
            print_error('Liczba błędów wynosi %d na %d pytań.' % (errors_count, self.tests_num))
            for (error_num, wrong_answer) in enumerate(self.wrong_answers, 1):
                expected = wrong_answer['expected']
                expected_options = ' lub '.join(expected)
                answer = wrong_answer['answer']
                question = wrong_answer['question']
                print_error('%d. W pytaniu "%s": "%s" -> "%s"' % (error_num, question, answer, expected_options))

    def make_question(self, dict_entry):
        lang = 'brazylijski' if self.tests_engine.ans_lang == 'br' else 'polski'
        return 'Przetłumacz na %s: "%s"' % (lang, dict_entry[self.tests_engine.ask_lang])

    def init_status(self, clear_cache):
        self.wrong_answers = []
        if clear_cache:
            self.cache = []


if __name__ == '__main__':
    with open(DICT_FILE, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        words_dict = WordsDict(csv_reader)

    repeat_mode = RepeatMode.REPEAT_NEW_PARAMS
    while repeat_mode != RepeatMode.NO_REPEAT:
        if repeat_mode == RepeatMode.REPEAT_NEW_PARAMS:
            words_dict.clear_filter()
            tests_num, ask_lang, ans_lang, chosen_groups, count = get_test_parameters(words_dict)
            words_dict.apply_filter(GroupFilter(chosen_groups).link(CountFilter(count)))
            words_test = WordsTest(words_dict, tests_num, ask_lang, ans_lang)

        repeat_previous_test = repeat_mode == RepeatMode.REPEAT_QUESTIONS
        words_test.test(repeat_previous_test)
        repeat_mode = choose_repeat_mode()
