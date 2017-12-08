#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to riotam_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
import os

import sys

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir, os.pardir, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from riotam_backend.common.MyDatabase import MyDatabase

replacement_dict = {
    'airfy-beacon': 'Airfy Beacon',
    'arduino-due': 'Arduino Due',
    'arduino-duemilanove': 'Arduino Duemilanove',
    'arduino-mega2560': 'Arduino Mega2560',
    'arduino-mkr1000': 'Arduino MKR1000',
    'arduino-mkrzero': 'Arduino MKR ZERO',
    'arduino-uno': 'Arduino Uno',
    'arduino-zero': 'Arduino Zero',
    'avsextrem': 'AVS Extrem',
    'b-l072z-lrwan1': 'B-L072Z-LRWAN1',
    'bluepill': 'Bluepill',
    'calliope-mini': 'Calliope Mini',
    'cc2538dk': 'CC2538DK',
    'cc2650-launchpad': 'CC2650 LaunchPad',
    'cc2650stk': 'CC2650STK',
    'chronos': 'eZ430 Chronos',
    'ek-lm4f120xl': 'EK-LM4F120XL',
    'f4vi1': 'F4VI1',
    'fox': 'HikoB Fox',
    'frdm-k22f': 'FRDM-K22F',
    'frdm-k64f': 'FRDM-K64F',
    'iotlab-a8-m3': 'IoT LAB A8-M3',
    'iotlab-m3': 'IoT LAB M3',
    'limifrog-v1': 'LimiFrog-v1',
    'maple-mini': 'Maple Mini',
    'mbed_lpc1768': 'mbed_lpc1768',
    'microbit': 'micro:bit',
    'mips-malta': 'MIPS Malta',
    'msb-430': 'MSB-430',
    'msb-430h': 'MSB-430H',
    'msba2': 'MSBA2',
    'msbiot': 'MSB-IoT',
    'mulle': 'Mulle',
    'nrf51dongle': 'nRF51 Dongle',
    'nrf52840dk': 'NRF52840DK',
    'nrf52dk': 'NRF52DK',
    'nrf6310': 'NRF6310',
    'nucleo-f030': 'Nucleo-F030',
    'nucleo-f070': 'Nucleo-F070',
    'nucleo-f072': 'Nucleo-F072',
    'nucleo-f091': 'Nucleo-F091',
    'nucleo-f103': 'Nucleo-F103',
    'nucleo-f302': 'Nucleo-F302',
    'nucleo-f303': 'Nucleo-F303',
    'nucleo-f334': 'Nucleo-F334',
    'nucleo-f401': 'Nucleo-F401',
    'nucleo-f410': 'Nucleo-F410',
    'nucleo-f411': 'Nucleo-F411',
    'nucleo-f446': 'Nucleo-F446',
    'nucleo-l053': 'Nucleo-L053',
    'nucleo-l073': 'Nucleo-L073',
    'nucleo-l152': 'Nucleo-L152',
    'nucleo-l476': 'Nucleo-L467',
    'nucleo144-f207': 'Nucleo144-F207',
    'nucleo144-f303': 'Nucleo144-F303',
    'nucleo144-f412': 'Nucleo144-F412',
    'nucleo144-f413': 'Nucleo144-F413',
    'nucleo144-f429': 'Nucleo144-F429',
    'nucleo144-f446': 'Nucleo144-F446',
    'nucleo144-f722': 'Nucleo144-F722',
    'nucleo144-f746': 'Nucleo144-F746',
    'nucleo144-f767': 'Nucleo144-F767',
    'nucleo32-f031': 'Nucleo144-F031',
    'nucleo32-f042': 'Nucleo144-F042',
    'nucleo32-f303': 'Nucleo144-F303',
    'nucleo32-l031': 'Nucleo144-F031',
    'nucleo32-l432': 'Nucleo144-F432',
    'nz32-sc151': 'NZ32-SC151',
    'opencm904': 'OpenCM9.04',
    'openmote-cc2538': 'OpenMote',
    'pba-d-01-kw2x': 'Phytec phyWAVE-KW22',
    'pca10000': 'PCA10000',
    'pca10005': 'PCA10005',
    'pic32-clicker': 'PIC32 Clicker',
    'pic32-wifire': 'PIC32 WiFire',
'qemu-i386': 'qemu-i386',
    'remote-pa': 'Zolertia remote (Prototype)',
    'remote-reva': 'Zolertia remote (Rev. A)',
    'remote-revb': 'Zolertia remote (Rev. B)',
    'samd21-xpro': 'SAMD21-xpro',
    'saml21-xpro': 'SAML21-xpro',
    'samr21-xpro': 'SAMR21-xpro',
    'seeeduino_arch-pro': 'Seeeduino Arch-Pro',
    'slwstk6220a': 'SLWSSTK6220A',
    'sodaq-autonomo': 'SODAQ Autonomo',
    'sodaq-explorer': 'SODAQ ExpLoRer',
    'spark-core': 'Spark Core',
    'stm32f0discovery': 'STM32F0discovery',
    'stm32f3discovery': 'STM32F3discovery',
    'stm32f4discovery': 'STM32F4discovery',
    'stm32f7discovery': 'STM32F7discovery',
    'telosb': 'TelosB',
    'udoo': 'UDOO',
    'waspmote-pro': 'Waspmote Pro',
    'wsn430-v1_3b': 'WSN430 (v1_3b)',
    'wsn430-v1_4': 'WSN430 (v1_4)',
    'yunjia-nrf51822': 'yunjia-nrf51822',
    'z1': 'Zolertia Z1',
}

db = MyDatabase()


def main():

    sql = 'UPDATE boards SET display_name=%s WHERE internal_name=%s;'

    for internal_name, display_name in replacement_dict.iteritems():

        constructed_display_name = display_name + ' (%s)' % internal_name
        db.query(sql, (constructed_display_name, internal_name))

    db.commit()


if __name__ == '__main__':

    main()
