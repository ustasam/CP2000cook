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

    os.chdir(os.path.dirname(sys.argv[0]))

    print ""
    if len(sys.argv) == 1:
        sys.argv.append("main")  # default command

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    main_parser = subparsers.add_parser('main', help='GUI program')
    main_parser.add_argument('--recipe', '-r', action='store', help='Recipe path')
    main_parser.add_argument('--emulate', action='store_true', help='Emulate instrument')
    main_parser.add_argument('--datadir', action='store', help='Main data directory')
    main_parser.add_argument('--showdebug', action='store_true', help='Print debug messages')

    # test_parser = subparsers.add_parser('cook', help='Cook recipe')
    # test_parser.add_argument('--recipe', '-r', action='store', help='Recipe path')
    # test_parser.add_argument('--parameter', '-p', action='store', help='Recipe parameter')

    # reglist_parser = subparsers.add_parser('reglist', help='Print main cp2000 registers')

    test_parser = subparsers.add_parser('cp2000_test', help='Make test operation on cp2000')

    parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + "1.1a")

    args = parser.parse_args()

    #
    print("Welocome to cp2000. v1.0.")

    format = '%(asctime)s %(levelname)-8s %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        filename=config.logfile,
        encoding="UTF-8",
        level=config.logLevel,
        datefmt=datefmt,
        format=format)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(format))
    logging.getLogger().addHandler(ch)

    logging.info("")
    logging.info("Main started.")

    if args.command == "main":

            config.print_debug = args.showdebug
            config.emulate_instrument = (args.emulate or config.emulate_instrument)

            if args.recipe is not None:
                if not os.path.isfile(args.recipe):
                    print("Error: File \"" + args.recipe + "\" is not exist.")
                    exit(1)
                args.recipe = args.recipe.decode(sys.getfilesystemencoding())

            if args.datadir is not None:
                if not os.path.isdir(args.datadir):
                    print("Error: Directory \"" + args.datadir + "\" is not exist.")
                    exit(1)

                config.config_files(args.datadir.decode(sys.getfilesystemencoding()).rstrip('/\\'))

            if config.emulate_instrument:
                instrument = None
            else:
                instrument = cp2000.CP2000.get_instrument(config.PORT,
                                                          config.ADDRESS,
                                                          config.minimalmodbus_mode)
                if not instrument:
                    logging.error("Нет связи с прибором.")
                    dialog.infoDialog(
                        "Нет связи с прибором.", explains="Не удается установить соединение с прибором. " +
                        "Проверьте целостность кабеля и настройки программы.")
                    exit(1)

            program.run_main(instrument, args.recipe)

    elif args.command == "cp2000_test":
        cp2000.cp2000_communication_test()

    elif args.command == "cook":
        print("The command hasn't been released yet.")

    elif args.command == "reglist":
        print("The command hasn't been released yet.")
