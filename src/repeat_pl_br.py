#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv

from communication import choose_groups, get_last_translations, get_tests_lang, get_tests_num
from randomizer import AvoidRepeatRandomizer, SimpleRandomizer
from utils import get_fake_file, print_error, print_info, print_ok


DICT_FILE = 'pt_br_words.csv'


class WordsDict:
    def __init__(self, csv_reader, max_translations=None):
        self.translations = []
        for line in csv_reader:
            try:
                pl, br, en, group = line
            except ValueError:
                line_num = csv_reader.line_num
                print 'WordsDict - unable to read line no %d = %s' % (line_num, line)
                raise
            translation = {
                'pl': pl,
                'br': br,
                'en': en,
                'group': group,
            }
            self.translations.append(translation)

        if max_translations:
            self.translations = self.translations[-max_translations:]

    def __len__(self):
        return len(self.translations)

    def __getitem__(self, index):
        return self.translations[index]

    def get_groups(self):
        return {translation['group'] for translation in self.translations}

    @staticmethod
    def from_string_io(string_io, max_translations=None):
        fake_file = get_fake_file(string_io)
        reader = csv.reader(fake_file, delimiter=';')
        words_dict = WordsDict(reader, max_translations)
        return words_dict


class WordsTestEngine:
    def __init__(self, words_dict, pl_to_br=False, avoid_repeat=True):
        self.words_dict = words_dict
        if pl_to_br:
            self.ask_field = 'pl'
            self.ans_field = 'br'
        else:
            self.ask_field = 'br'
            self.ans_field = 'pl'

        if avoid_repeat:
            self.randomizer = AvoidRepeatRandomizer(0, len(self.words_dict) - 1)
        else:
            self.randomizer = SimpleRandomizer(0, len(self.words_dict) - 1)

    def get_dict_entry(self, index=None):
        index = self.randomizer.next_random() if index is None else index
        return self.words_dict[index]

    def get_expected_answers(self, dict_entry):
        expected_answers_list = dict_entry[self.ans_field]
        expected_answers = expected_answers_list.split('|')
        lowered_expected_answers = map(str.lower, expected_answers)
        return lowered_expected_answers

    def get_error(self, dict_entry, answer):
        lowered_answer = answer.lower()
        expected_answers = self.get_expected_answers(dict_entry)
        if lowered_answer not in expected_answers:
            question = dict_entry[self.ask_field]
            return {
                'expected': expected_answers,
                'answer': answer,
                'question': question,
            }
        else:
            return None


class WordsTest:
    def __init__(self, words_dict, tests_num, pl_to_br=False, quick_feedback=True):
        self.tests_engine = WordsTestEngine(words_dict, pl_to_br)
        self.tests_num = tests_num
        self.init_status()
        self.quick_feedback = quick_feedback

    def test(self):
        self.init_status()
        for test_num in range(self.tests_num):
            dict_entry = self.tests_engine.get_dict_entry()
            self.ask_question(dict_entry)
            answer = self.read_answer(dict_entry)
            self.update_status(dict_entry, answer)

        self.present_results()

    def ask_question(self, dict_entry):
        question = self.make_question(dict_entry)
        print_info(question)

    def read_answer(self, dict_entry):
        lang = 'brazylijsku' if self.tests_engine.ans_field == 'br' else 'polsku'
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
        lang = 'brazylijski' if self.tests_engine.ans_field == 'br' else 'polski'
        return 'Przetłumacz na %s: "%s"' % (lang, dict_entry[self.tests_engine.ask_field])

    def init_status(self):
        self.wrong_answers = []


if __name__ == '__main__':
    tests_num = get_tests_num()
    lang_dict = get_tests_lang()
    count = get_last_translations()
    if lang_dict['from'] == 'pl' and lang_dict['to'] == 'pt':
        pl_to_br = True
    elif lang_dict['from'] == 'pt' and lang_dict['to'] == 'pl':
        pl_to_br = False
    else:
        raise ValueError('Nieznany opis testowych języków %s -> %s' % (lang_dict['from'], lang_dict['to']))

    with open(DICT_FILE, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        words_dict = WordsDict(csv_reader, count)

    groups = list(words_dict.get_groups())
    chosen_groups = choose_groups(groups)
    print chosen_groups

    words_test = WordsTest(words_dict, tests_num, pl_to_br)
    words_test.test()
