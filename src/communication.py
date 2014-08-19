#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import i18n
_ = i18n.language.ugettext


class RepeatMode:
    REPEAT_QUESTIONS = 1
    REPEAT_OLD_PARAMS = 2
    REPEAT_NEW_PARAMS = 3
    NO_REPEAT = 4
    MAPPING = {
        1: REPEAT_QUESTIONS,
        2: REPEAT_OLD_PARAMS,
        3: REPEAT_NEW_PARAMS,
        4: NO_REPEAT,
    }

    @staticmethod
    def from_number(number):
        return RepeatMode.MAPPING[number]


def get_test_parameters(words_dict):
    tests_num = get_tests_num()
    ask_lang, ans_lang = get_tests_lang(words_dict.get_langs())
    groups = words_dict.get_groups()
    chosen_groups = choose_groups(groups)
    count = get_last_translations(len(words_dict))

    return (tests_num, ask_lang, ans_lang, chosen_groups, count, )


def get_int_in_range(question, min_val=-sys.maxint - 1, max_val=sys.maxint, default=None):
    encoded_question = question.encode('utf-8') if isinstance(question, unicode) else question
    answer_str = raw_input(encoded_question)
    if not answer_str and default is not None:
        answer = default
    else:
        try:
            answer = int(answer_str)
        except ValueError:
            print u'Given value %s is not a number' % answer_str
            raise

    if answer < min_val or max_val < answer:
        raise ValueError('Given number %d is not in range [%d;%d]' % (answer, min_val, max_val))

    return answer


def get_tests_num():
    question_msg = _(u'Enter number of questions that you want to answer (default all in selected groups): ')
    tests_num = get_int_in_range(question_msg, 1, default=sys.maxint)
    return tests_num


def print_ask_languages(langs):
    print _(u'Choose questions language')
    for (i, lang) in enumerate(langs, 1):
        print '%d) %s' % (i, lang)


def print_ans_languages(langs):
    print _(u'Choose answers language')
    for (i, lang) in enumerate(langs, 1):
        print '%d) %s' % (i, lang)


def get_tests_lang(langs):
    print_ask_languages(langs)
    question_msg = _(u'Choose option number: ')
    ask_lang_index = get_int_in_range(question_msg, 1, len(langs)) - 1
    ask_lang = langs[ask_lang_index]

    possible_ans_langs = filter(lambda lang: lang != ask_lang, langs)
    print_ans_languages(possible_ans_langs)
    ans_lang_index = get_int_in_range(question_msg, 1, len(possible_ans_langs)) - 1
    ans_lang = possible_ans_langs[ans_lang_index]

    return ask_lang, ans_lang


def get_last_translations(maximal_count):
    question_msg = _(u'How many recent words you want to examine (default all)? : ')
    count = get_int_in_range(question_msg, min_val=1, default=maximal_count)
    return count


def choose_groups(groups_set):
    groups = list(groups_set)
    print _(u'Which groups you want to examine (e.g. 1,3-5)? : ')
    for (num, group) in enumerate(groups, 1):
        print '%d) %s' % (num, group)

    groups_str = raw_input(_(u'Groups: ').encode('utf-8'))

    split_groups = groups_str.split(u',')
    chosen_groups = set()
    for group_str in split_groups:
        if u'-' in group_str:
            start, end = parse_range(group_str)
            for group_name in groups[start:end + 1]:
                chosen_groups.add(group_name)
        else:
            try:
                group_nr = int(group_str) - 1
            except ValueError:
                print u'Group number %s is not a number' % group_str
                raise
            chosen_groups.add(groups[group_nr])

    return chosen_groups or groups_set


def parse_range(range_str):
    range_split = range_str.split('-', 1)
    try:
        start = int(range_split[0]) - 1
        end = int(range_split[1]) - 1
    except ValueError:
        print 'One of values %s, %s is not a number' % (range_split[0], range_split[1])
        raise
    return start, end


def print_repeat_mode():
    print _(u'Do you want to repeat test?')
    print _(u'1) Yes, with the same questions')
    print _(u'2) Yes, with the same parameters, but questions drawn again')
    print _(u'3) Yes, with different parameters')
    print _(u'4) No')


def choose_repeat_mode():
    print_repeat_mode()
    repeat_mode = get_int_in_range(_(u'Choose option number: '), 1, 4, 1)
    return RepeatMode.from_number(repeat_mode)
