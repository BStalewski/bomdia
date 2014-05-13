#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
    lang_dict = get_tests_lang()
    if lang_dict['from'] == 'pl' and lang_dict['to'] == 'pt':
        pl_to_br = True
    elif lang_dict['from'] == 'pt' and lang_dict['to'] == 'pl':
        pl_to_br = False
    else:
        raise ValueError('Nieznany opis testowych języków %s -> %s' % (lang_dict['from'], lang_dict['to']))
    groups = words_dict.get_groups()
    chosen_groups = choose_groups(groups)
    count = get_last_translations(len(words_dict))

    return (tests_num, pl_to_br, chosen_groups, count, )


def get_tests_num():
    tests_num_ans = raw_input('Podaj liczbę testów, którą chcesz wykonać: ')
    try:
        tests_num = int(tests_num_ans)
    except ValueError:
        print 'Podana liczba testów (%s) nie jest liczbą' % tests_num_ans
        raise

    return tests_num


def print_tests_variants():
    print 'Możesz testować następujące kombinacje:'
    print '1) polski      -> portugalski'
    print '2) portugalski -> polski'


def get_tests_lang():
    print_tests_variants()
    test_variant_ans = raw_input('Wybierz numer opcji: ')
    try:
        test_variant = int(test_variant_ans)
    except ValueError:
        print 'Podany numer opcji (%s) nie jest liczbą' % test_variant_ans
        raise

    if test_variant == 1:
        return {
            'from': 'pl',
            'to': 'pt',
        }
    elif test_variant == 2:
        return {
            'from': 'pt',
            'to': 'pl',
        }
    else:
        raise ValueError('Nieakceptowany numer opcji %d' % test_variant)


def get_last_translations(maximal_count):
    str_count = raw_input('Wybierz, ile ostatnich słówek chcesz przetestować (domyślnie wszystkie): ')
    try:
        count = int(str_count)
    except ValueError:
        if str_count != '':
            print 'Błędnie podana liczba. Test będzie oparty o wszystkie słówka'
        count = maximal_count

    return count


def choose_groups(groups_set):
    groups = list(groups_set)
    print 'Wybierz, które grupy słów chcesz sprawdzić (np. 1,3-5)'
    for (num, group) in enumerate(groups, 1):
        print '%d) %s' % (num, group)

    groups_str = raw_input('Grupy: ')

    split_groups = groups_str.split(',')
    chosen_groups = set()
    for group_str in split_groups:
        if '-' in group_str:
            group_split = group_str.split('-', 1)
            try:
                start = int(group_split[0]) - 1
                end = int(group_split[1]) - 1
            except ValueError:
                print 'Jedna z wartości %s, %s nie jest liczbą' % (start, end)
                raise
            for group_name in groups[start:end + 1]:
                chosen_groups.add(group_name)
        else:
            try:
                group_nr = int(group_str) - 1
            except ValueError:
                print 'Numer grupy %s nie jest liczbą' % group_str
                raise
            chosen_groups.add(groups[group_nr])

    return chosen_groups or groups_set


def print_repeat_mode():
    print 'Czy chcesz powtórzyć test?'
    print '1) Tak, z dokładnie tymi samymi pytaniami'
    print '2) Tak, z tymi samymi parametrami, ale ponownie wylosowanymi pytaniami'
    print '3) Tak, z innymi parametrami'
    print '4) Nie'


def choose_repeat_mode():
    print_repeat_mode()
    repeat_mode_str = raw_input('Wybierz numer opcji: ')
    try:
        repeat_mode = int(repeat_mode_str)
    except ValueError:
        print 'Podany numer opcji jest błędny'
        raise

    if repeat_mode < 1 or 4 < repeat_mode:
        raise ValueError('Nieakceptowany numer opcji %d' % repeat_mode)

    return RepeatMode.from_number(repeat_mode)
