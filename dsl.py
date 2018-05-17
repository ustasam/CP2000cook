# -*- coding: utf-8 -*-

import dialog
from lark import Lark

gramamr = u'''

            start: instruction+

            code_block: "{" instruction+ "}"

            instruction: ("Пауза"i | "Pause"i) [CTIME] -> pause
                       | ("Имя"i | "Name"i | "Заголовок"i) ESCAPED_STRING -> program_name
                       | ("Параметр"i | "Parameter"i) IDENTIFIER [" "VALUE] [" "ESCAPED_STRING]  -> parameter
                       | ("Сообщение"i | "Message"i) ESCAPED_STRING [" "NUMBER] [" "ESCAPED_STRING] -> message
                       | ("Гудок"i | "Beep"i) [INT][" "INT][" "INT][" "INT] -> beep
                       | ("Операция"i | "Operate"i) VALUE ESCAPED_STRING CTIME [" "CTIME] -> operate
                       | ("Повторить"i |"Repeat"i) VALUE code_block -> repeat
                       | ("Конец"i | "End"i) -> end
                       | IDENTIFIER "=" sum -> expression

             ?sum: product
                 | sum "+" product   -> add
                 | sum "-" product   -> sub

             ?product: item
                 | product "*" item  -> mul
                 | product "/" item  -> div

             ?item: NUMBER           -> constant
                 | IDENTIFIER        -> identifier
                 | "-" item          -> neg
                 | "(" sum ")"


            IDENTIFIER: /[_A-zА-Яа-я]([\._A-zА-Яа-я0-9])*/
            NUMBER : ( SIGNED_INT"."INT | SIGNED_INT )
            VALUE: NUMBER | IDENTIFIER | ESCAPED_STRING
            CTIME: [[INT":"]INT":"]INT

            COMMENT: "/*" /(.|\\n|\\r)+/ "*/"
                     |  "#" /(.)+/ NEWLINE
                     |  "//" /(.)+/ NEWLINE

            %import common.ESCAPED_STRING
            %import common.SIGNED_INT
            %import common.NEWLINE
            %import common.LETTER
            %import common.INT
            %import common.WS

            %ignore WS
            %ignore COMMENT

        '''

parser = Lark(gramamr, ambiguity='explicit')


def parse(text):
    return parser.parse(text)


def direction(direction_value=True):
    return direction_value in [1, True] or \
            str(direction_value).lower() in ["1", "вперед", "forward", "true", "да", "yes"]


command_description = {
    'program_name': {'loc_name': "Имя программы",  'arguments': (('name', 'Имя', ""),)},
    'pause': {'loc_name': "Пауза", 'arguments': (('duration', 'Продолжительность', 1),)},
    'end': {'loc_name': "Конец", 'arguments': ()},
    'parameter': {'loc_name': "Параметер", 'arguments': (
        ('name', 'Имя', ""),
        ('default', 'Начальное', ""), ('message', 'Сообщение', "Введите значение"))},
    'message': {'loc_name': "Сообщение", 'arguments': (
        ('message', 'Сообщение', ""),
        ('duration', 'Продолжительность', 0), ('message2', 'Сообщение2', ""))},
    'beep': {'loc_name': "Гудок", 'arguments': (
        ('frequency', 'Частота', 3000), ('duration', 'Продолжительность', 1),
        ('count', 'Число раз', 1), ('pause', 'Длина паузы', 1))},
    'operate': {'loc_name': "Операция", 'arguments': (
            ('frequency', 'Частота', 10), ('direction', 'Направление', "Вперед"),
            ('time', 'Время', 10), ('rising_time', 'Время возрастания', 1))},
    'repeat': {'loc_name': "Повторить", 'arguments': (('count', 'Число раз', 1),)},
    'expression': {'loc_name': "Выражение", 'arguments': ()}
                       }

name_pos = 0
loc_name_pos = 1
default_value_pos = 2


def arg(node, position=0, default=""):
    if len(node.children) > position:
        val = node.children[position].value
        print node.children[position].name
        if isinstance(default, int):
            return int(val)
        elif isinstance(default, float):
            return float(val)
        else:
            return val
    return default


def args(node, defaults):
    result = ()
    for pos, item in enumerate(defaults):
        a = arg(node, pos, defaults[pos])
        result = result + (a,)
    return result


def arg_count(node):
    return len(node.children)


def get_command_loc_name(command_name):
    if command_name in command_description:
        return command_description[command_name]['loc_name']
    else:
        return command_name


def get_command_arguments(node):
    result = {}

    if node.name in command_description:
        arg_des = command_description[node.name]['arguments']

        for pos, item in enumerate(arg_des):
            result[item[name_pos]] = arg(node, pos, item[default_value_pos])

    return result
