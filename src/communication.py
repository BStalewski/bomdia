#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


def get_last_translations():
    str_count = raw_input('Wybierz, ile ostatnich słówek chcesz przetestować (domyślnie wszystkie): ')
    try:
        count = int(str_count)
    except ValueError:
        if str_count != '':
            print 'Błędnie podana liczba. Test będzie oparty o wszystkie słówka'
        count = None

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
                start = int(group_split[0])
                end = int(group_split[1])
            except ValueError:
                print 'Jedna z wartości %s, %s nie jest liczbą' % (start, end)
                raise
            for group_name in groups[start:end + 1]:
                chosen_groups.add(group_name)
        else:
            try:
                group_nr = int(group_str)
            except ValueError:
                print 'Numer grupy %s nie jest liczbą' % group_str
                raise
            chosen_groups.add(groups[group_nr])

    return chosen_groups
