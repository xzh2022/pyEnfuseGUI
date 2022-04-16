# -*- coding: utf-8 -*-

# program_texts.py - This python helper scripts holds longer texts for popups and the like

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import PySimpleGUI as sg

Version = '0.1.0'
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

def about_popup():
    #window.disappear()
    sg.popup('About pyImgFuse, Version ' + Version + '\n\n',
             'pyImgFuse is a program to do this and that and much more.',
             'It uses enfuse, align_image_stack and exiftool to do that.', grab_anywhere=True, keep_on_top=True)
    #window.reappear()
