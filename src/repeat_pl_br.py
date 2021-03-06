#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv

from filters import CountFilter, GroupFilter
from communication import get_test_parameters, choose_repeat_mode, RepeatMode
from randomizer import AvoidRepeatRandomizer, SimpleRandomizer
from utils import get_fake_file, print_error, print_info, print_ok

import i18n
_ = i18n.language.ugettext


DICT_FILE = u'translations.csv'

'''
1. Złączony słownik budowany dla wybranej pary języków, nie dla wszystkich od razu.
2. Złączony słownik cachowany - po wybraniu pary jest zapisywany i używany ponownie.
3. Brakuje znaków symbolizujących lub ("|") w pliku źródłowym.
4. W złączonym słowniku nie ma symboli "|" w języku źródłowym.
TODO:
- nowy format tłumaczeń
- przy odpowiedziach z wieloma tłumaczeniami, podawać alternatywy
'''


class WordsDict:
    GROUP_KEY = u'group'

    def __init__(self, csv_reader):
        self.all_translations = []
        try:
            self.header = next(csv_reader)
        except StopIteration:
            raise ValueError(u'WordsDict - empty file')

        if self.GROUP_KEY not in self.header:
            raise ValueError(u'WordsDict - incorrect header - missing %s field' % (self.GROUP_KEY,))

        for (i, line) in enumerate(csv_reader, 1):
            if len(self.header) != len(line):
                line_num = csv_reader.line_num
                raise ValueError(u'WordsDict - wrong fields (%s) number in line %d.' % (line, line_num))

            unicode_line = [self.to_utf8(field) for field in line]
            translation = dict(zip(self.header, unicode_line))
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

    def to_utf8(self, value):
        try:
            return value.decode('utf-8')
        except UnicodeEncodeError:
            return value

    @staticmethod
    def from_string_io(lines):
        fake_file = get_fake_file(lines)
        reader = csv.reader(fake_file, delimiter=';')
        words_dict = WordsDict(reader)
        return words_dict


class WordsTestEngine:
    def __init__(self, words_dict, ask_lang, ans_lang, avoid_repeat=True):
        if ask_lang == ans_lang:
            raise ValueError(u'Answer language cannot be the same as answer language (%s)' % ask_lang)
        self.words_dict = words_dict
        self.ask_lang = ask_lang
        self.ans_lang = ans_lang

        if avoid_repeat:
            self.randomizer = AvoidRepeatRandomizer(0, len(self.words_dict) - 1)
        else:
            self.randomizer = SimpleRandomizer(0, len(self.words_dict) - 1)

    def reset(self):
        self.randomizer.reset()

    def get_dict_entry(self, index=None):
        index = self.randomizer.next_random() if index is None else index
        return self.words_dict[index]

    def get_expected_answers(self, dict_entry):
        expected_answers_list = dict_entry[self.ans_lang]
        expected_answers = expected_answers_list.split(u'|')
        lowered_expected_answers = map(lambda s: s.lower(), expected_answers)
        return lowered_expected_answers

    def get_error(self, dict_entry, answer):
        lowered_answer = answer.lower()
        expected_answers = self.get_expected_answers(dict_entry)
        if lowered_answer not in expected_answers:
            question = dict_entry[self.ask_lang]
            return {
                u'expected': expected_answers,
                u'answer': answer,
                u'question': question,
            }
        else:
            return None


class WordsTest:
    def __init__(self, words_dict, tests_num, ask_lang, ans_lang, quick_feedback=True):
        self.tests_engine = WordsTestEngine(words_dict, ask_lang, ans_lang)
        self.tests_num = min(tests_num, len(words_dict))
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
        answer = raw_input('%s: ' % self.tests_engine.ans_lang).decode(u'utf-8')
        return answer

    def update_status(self, dict_entry, answer):
        error = self.tests_engine.get_error(dict_entry, answer)
        if error:
            self.wrong_answers.append(error)

        if self.quick_feedback:
            self.present_quick_feedback(error)

    def present_quick_feedback(self, error):
        if error:
            answer = error[u'answer']
            expected = error[u'expected']
            msg_or = _(u' or ')
            expected_options = msg_or.join(expected)
            msg_error = _(u'Error: %(ans)s -> %(exp)s') % {u'ans': answer, u'exp': expected_options}
            print_error(msg_error)
        else:
            print_ok(u'OK')

    def present_results(self):
        errors_count = len(self.wrong_answers)
        if errors_count == 0:
            print_ok(_(u'Perfect! No errors!!!'))
        else:
            print_error(_(u'Unfortunately, there were errors'))
            msg_summary = (_(u'Number of errors is %(errors)d for %(questions)d questions.') %
                           {u'errors': errors_count, u'questions': self.tests_num})
            print_error(msg_summary)
            for (error_num, wrong_answer) in enumerate(self.wrong_answers, 1):
                expected = wrong_answer[u'expected']
                expected_options = _(u' or ').join(expected)
                answer = wrong_answer[u'answer']
                question = wrong_answer[u'question']

                explanation_msg = (_(u'%(num)d. In question "%(question)s": "%(ans)s" -> "%(expected)s"') %
                                   {u'num': error_num, u'question': question,
                                    u'ans': answer, u'expected': expected_options})
                print_error(explanation_msg)

    def make_question(self, dict_entry):
        question = (_(u'Translate into %(ans)s: "%(ask)s"') %
                    {u'ans': self.tests_engine.ans_lang, u'ask': dict_entry[self.tests_engine.ask_lang]})
        return question

    def init_status(self, clear_cache):
        self.tests_engine.reset()
        self.wrong_answers = []
        if clear_cache:
            self.cache = []


if __name__ == u'__main__':
    with open(DICT_FILE, u'rb') as csv_file:
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
