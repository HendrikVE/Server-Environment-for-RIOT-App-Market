#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function

from shutil import copytree, rmtree, copyfile
import os
import config.strip_config as config


def main():
    
    try:
        if os.path.exists("RIOT_stripped"):
            rmtree("RIOT_stripped")
            
        copytree("RIOT", "RIOT_stripped", ignore=config.ignore_patterns)
        
        path = "RIOT_stripped/Makefile.include"
        # Save the old one to check later in case there is an error
        copyfile(path, path + '.old')

        with open(path + '.old', "r") as old_makefile:
            with open(path, "w") as makefile:
                for line in old_makefile.readlines():

                    if line.startswith("flash: all") or line.startswith("preflash: all"):
                        print('Changing lines:')
                        print('    %s' % line)
                        line = line.replace(" all", "")
                        print(' -> %s' % line)

                    makefile.write(line)

    except Exception as e:
        print (e)
        exit(1)


if __name__ == "__main__":

    main()
