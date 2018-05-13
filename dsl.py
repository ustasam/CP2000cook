# -*- coding: utf-8 -*-

import dialog
from lark import Lark

gramamr = u'''

            start: instruction+

            code_block: "{" instruction+ "}"

            instruction: ("Пауза"i | "Pause"i) [CTIME] -> pause
                       | ("Конец"i | "End"i) -> end
                       | ("Имя"i | "Name"i | "Заголовок"i) ESCAPED_STRING -> program_name
                       | ("Параметр"i | "Parameter"i) IDENTIFIER [" "VALUE] [" "VALUE] -> parameter
                       | ("Сообщение"i | "Message"i) VALUE [" "VALUE] [" "VALUE] -> message
                       | ("Гудок"i | "Beep"i) [INT][" "INT][" "INT][" "INT] -> beep
                       | ("Вращай"i | "Operate"i) VALUE VALUE VALUE [" "VALUE] -> operate
                       | ("Повторить"i |"Repeat"i) VALUE code_block -> repeat
                       | IDENTIFIER "=" sum -> expression

             ?sum: product
                 | sum "+" product   -> add
                 | sum "-" product   -> sub

             ?product: item
                 | product "*" item  -> mul
                 | product "/" item  -> div

             ?item: NUMBER           -> number
                 | IDENTIFIER        -> identifier
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


def parse_recipe_text(text, gui_message=False, print_pretty=False):
    tree = None
    try:
        tree = parser.parse(text)
    except Exception as err:
        print("Error in recipe file. \n" + str(err))
        if gui_message:
            dialog.infoDialog("Ошибка в разборе файла рецепта. \n" + str(err))
    if print_pretty and (tree is not None):
        print(tree.pretty())
        print(tree.children)

    return tree
