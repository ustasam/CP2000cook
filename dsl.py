# -*- coding: utf-8 -*-

from lark import Lark

gramamr = u'''

            start: instruction+

            code_block: "{" instruction+ "}"

            instruction: ("Пауза"i | "Pause"i) [CTIME] -> pause
                       | ("Конец"i | "End"i) -> end
                       | ("Имя"i | "Name"i | "Заголовок"i) ESCAPED_STRING -> program_name
                       | ("Параметр"i | "Parameter"i) IDENTIFIER [VALUE] [VALUE] -> parameter
                       | ("Сообщение"i | "Message"i) VALUE [VALUE] [VALUE] -> message
                       | ("Гудок"i | "Beep"i) VALUE VALUE [VALUE] [VALUE] -> beep
                       | ("Вращай"i | "Operate"i) VALUE VALUE VALUE [VALUE] -> operate
                       | ("Повторить"i |"Repeat"i) VALUE code_block -> repeat
                       | IDENTIFIER "=" sum -> expression

             ?sum: product
                 | sum "+" product   -> add
                 | sum "-" product   -> sub

             ?product: item
                 | product "*" item  -> mul
                 | product "/" item  -> div

             ?item: NUMBER           -> number
                 | IDENTIFIER        ->  identifier
                 | "-" item          -> neg
                 | "(" sum ")"


            IDENTIFIER: /[_A-zА-Яа-я]([\._A-zА-Яа-я0-9])*/
            NUMBER : ( SIGNED_INT"."INT | SIGNED_INT )
            VALUE: ESCAPED_STRING | NUMBER | IDENTIFIER
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

parser = Lark(gramamr)

# test_text = u'''
#     Имя "Name4 Name5" #comment
#     Сообщение "Текст" "-"
#     Parameter Пар155 "Сообщение о вводе" 65.554
#     tt = 3 + 4 * (4 + 5 + Var34 * 8)
#     Вращай 2 12 "Вперед" 5 # Частота, Время, Направление, Время возрастания
#     Сообщение "Текст"
#     Гудок 8000 10 3
#     #comment
#     Пауза 4:6436:66
#     Пауза 55
#     Конец
#     Повторить 3 {
#         Сообщение "Текст"
#     }
# '''
#
# try:
#     parse = parser.parse(test_text)
# except Exception as err:
#     print err
# if parse is not None:
#     print(parse.pretty())
#     print(parse)
