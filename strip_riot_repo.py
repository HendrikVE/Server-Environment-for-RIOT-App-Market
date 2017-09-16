#!/usr/bin/python
# -*- coding: UTF-8 -*-

from shutil import copytree, rmtree
import os
import config.strip_config as config

def main():
    
    try:
        if os.path.exists("RIOT_stripped"):
            rmtree("RIOT_stripped")
            
        copytree("RIOT", "RIOT_stripped", ignore=config.ignore_patterns)
        
        path = "RIOT_stripped/Makefile.include"
        file_content = []
        with open(path, "r") as makefile:
            
            lines = makefile.readlines()
            
            for line in lines:
                file_content.append(line)
            
        with open(path, "w") as makefile:
            for line in file_content:
                
                if "flash: all" in line:
                    makefile.write(line.replace(" all", ""))
                else:
                    makefile.write(line)
                    
        
    except Exception as e:
        print e
        
if __name__ == "__main__":
    main()