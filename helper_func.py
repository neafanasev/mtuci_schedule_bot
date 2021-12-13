from datetime import date

def num_of_current_week(cur_date):
    current_week = cur_date.isocalendar()[1]
    first_week = date(2021, 9, 1).isocalendar()[1]
    return current_week - first_week

def get_day(n, cur_date):
    if num_of_current_week(cur_date) % 2 == 0:
        return n
    else:
        return n+6

def start_time(n):
    if n == 0:
        return '9:30-11:05'
    elif n == 1:
        return '11:20-12:55'
    elif n == 2:
        return '13:10-14:45'
    elif n == 3:
        return '15:25-17:00'
    else:
        return '17:15-18:50'

def subject_type(n):
    if n == 0:
        return 'лек.'
    elif n == 1:
        return 'лаб.'
    elif n == 2:
        return 'пр. з.'
    else:
        return ''

def weekday(n):
    if type(n) == type(29):
        if n == 0:
            return 'Понедельник'
        elif n == 1:
            return 'Вторник'
        elif n == 2:
            return 'Среда'
        elif n == 3:
            return 'Четверг'
        elif n == 4:
            return 'Пятница'
        else:
            return 'Суббота'
    else:
        if n == 'monday':
            return 0
        elif n == 'tuesday':
            return 1
        elif n == 'wednesday':
            return 2
        elif n == 'thursday':
            return 3
        elif n == 'friday':
            return 4
        else:
            return 5
