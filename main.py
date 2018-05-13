#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import argparse
import config
import program
import cp2000
import dialog

if __name__ == "__main__":

    print ""
    if len(sys.argv) == 1:
        sys.argv.append("main")  # default command

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    main_parser = subparsers.add_parser('main', help='GUI program')
    main_parser.add_argument('--recipe', '-r', action='store', help='Recipe path')
    main_parser.add_argument('--emulate', action='store_true',
                             help='Emulate instrument')

    test_parser = subparsers.add_parser('cook', help='Cook recipe')
    test_parser.add_argument('--recipe', '-r', action='store', help='Recipe path')
    test_parser.add_argument('--parameter', '-p', action='store', help='Recipe parameter')

    reglist_parser = subparsers.add_parser('reglist', help='Print main cp2000 registers')

    test_parser = subparsers.add_parser('cp2000_test', help='Make test operation on cp2000')

    parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + "1.0a")

    args = parser.parse_args()

    #
    print("Welocome to cp2000. v1.0.")

    format = '%(asctime)s %(levelname)-8s %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        filename=config.logfile,
        level=config.logLevel,
        datefmt=datefmt,
        format=format)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(format))
    logging.getLogger().addHandler(ch)

    logging.info("")
    logging.info("Main started.")

    if args.command == "main":

            if args.recipe is not None:
                if not os.path.isfile(args.recipe):
                    print("Error: file \"" + args.recipe + "\" not exist.")
                    exit(1)

                args.recipe = args.recipe.decode(sys.getfilesystemencoding()).encode("utf-8")

            config.emulate_instrument = (args.emulate or config.emulate_instrument)

            instrument = None if config.emulate_instrument else \
                cp2000.CP2000.get_instrument(config.PORT, config.ADDRESS, config.minimalmodbus_mode)

            if instrument is not None or config.emulate_instrument:

                program.main(instrument, args.recipe)

            else:
                logging.error("Нет связи с прибором.")
                dialog.infoDialog(
                    "Нет связи с прибором.", explains="Не удается установить соединение с прибором. " +
                    "Проверьте целостность кабеля и настройки программы.")

    elif args.command == "cp2000_test":
        cp2000.cp2000_communication_test()

    elif args.command == "cook":
        print("The command hasn't been released yet.")

    elif args.command == "reglist":
        print("The command hasn't been released yet.")
