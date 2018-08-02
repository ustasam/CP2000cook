# -*- coding: utf-8 -*-

from lark import Lark
import re

# Lark - a modern parsing library for Python
# https://github.com/lark-parser/lark

gramamr = u'''

    start: instruction+

    code_block: "{" instruction+ "}"

    instruction: \
          ("Имя"i | "Name"i | "Заголовок"i) ESCAPED_STRING -> program_name
        | ("Конец"i | "End"i) -> end
        | ("Остановить"i | "Stop"i) -> stop
        | ("Сообщение"i | "Message"i) ESCAPED_STRING -> message

        | ("ОкноСообщения"i | "MessageDialog"i) ESCAPED_STRING -> message_dialog
        | ("ОкноВвода"i | "InputDialog"i) IDENTIFIER [" "VALUE | ESCAPED_STRING] [" "ESCAPED_STRING]  -> input
        | ("Ожидание"i | "Wait"i | "Пауза"i | "Pause"i | \
            "Подтверждение"i | "Confirmation"i) [CTIME] [ESCAPED_STRING] -> wait

        | ("Гудок"i | "Beep"i | "Звук"i | "Sound"i) [INT][" "INT][" "INT][" "INT] -> beep
        | ("Операция"i | "Operate"i) VALUE ESCAPED_STRING CTIME [" "CTIME] -> operate
        | ("Повторить"i |"Repeat"i) VALUE code_block -> repeat

        | ("ОтчетПриход"i |"ReportComing"i) ESCAPED_STRING ESCAPED_STRING VALUE -> coming
        | ("ОтчетРасход"i |"ReportConsumption"i) ESCAPED_STRING ESCAPED_STRING VALUE -> consumptions

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
    VALUE: NUMBER | IDENTIFIER
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


command_description = {
    'program_name': {'loc_name': "Имя программы",  'arguments': (('name', 'Имя', ""),)},
    'end': {'loc_name': "Конец", 'arguments': ()},
    'stop': {'loc_name': "Остановить", 'arguments': ()},

    'message': {'loc_name': "Сообщение", 'arguments': (('message', 'Сообщение', ""),)},
    'message_dialog': {'loc_name': "Окно сообщения", 'arguments': (('message', 'Сообщение', ""),)},
    'input': {'loc_name': "Окно ввода", 'arguments': (
        ('name', 'Имя', ""),
        ('default', 'Начальное', ""), ('message', 'Сообщение', "Введите значение"))},

    'wait': {'loc_name': "Ожидание", 'arguments': (
        ('duration', 'Продолжительность', 1),
        ('message', 'Сообщение', ""))},

    'beep': {'loc_name': "Гудок", 'arguments': (
        ('frequency', 'Частота', 3000), ('duration', 'Продолжительность', 1),
        ('count', 'Число раз', 1), ('pause', 'Длина паузы', 1))},
    'operate': {'loc_name': "Операция", 'arguments': (
            ('frequency', 'Частота', 10), ('direction', 'Направление', "Вперед"),
            ('time', 'Время', 5), ('rising_time', 'Время возрастания', 1))},
    'repeat': {'loc_name': "Повторить", 'arguments': (('count', 'Число раз', 1),)},

    'coming': {'loc_name': "ОтчетПриход", 'arguments': (
        ('report_name', 'Имя отчета', ""), ('value_name', 'Имя прихода', ""))},
    'consumptions': {'loc_name': "ОтчетРасход", 'arguments': (
        ('report_name', 'Имя отчета', ""), ('value_name', 'Имя расхода', ""))},

    'expression': {'loc_name': "Выражение", 'arguments': ()}
}

name_pos = 0
loc_name_pos = 1
default_value_pos = 2


def arg(node, position=0, default=""):
    if len(node.children) > position:
        val = node.children[position].value

        if isinstance(default, int):
            return int(val)
        elif isinstance(default, float):
            return float(val)
        else:
            if node.children[position].type == "ESCAPED_STRING":
                return val[1:-1]  # remove quotes
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


def fill_identifiers(args, identifiers):
    res = {}
    for key, value in args.iteritems():
        if type(value) == unicode or type(value) == str:

            templates = re.findall('%(.+?)%', value)

            for template in templates:

                if template in identifiers:
                    value = value.replace(u"%" + template + u"%",
                                          unicode(identifiers[template]))
            res[key] = value
        else:
            res[key] = value
    return res


def direction(direction_value=True):
    return direction_value in [1, True] or \
            unicode(direction_value).lower() in [u"1", u"вперед", u"forward", u"true", u"да", u"yes"]
