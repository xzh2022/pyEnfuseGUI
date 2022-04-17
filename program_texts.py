# -*- coding: utf-8 -*-

# program_texts.py - This python helper scripts holds longer texts for popups and the like.
# It also contains a few functions to assist with this longer texts.

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

import image_functions

# Some program constants
Version = '0.2.0'
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

################ Some Function #################
def popup_text_scroll(title, message, scrollmessage):
    layout = [
        [sg.Text(message)],
        #[sg.ScrolledText(scrollmessage)],
        [sg.Multiline(scrollmessage, size=(80, 15), font='Courier 10', expand_x=True, expand_y=True, write_only=True,
                       autoscroll=True, auto_refresh=True)],
        [sg.Button('OK. Understood', key='-close_popup_text_scroll-')]
    ]
    ptswindow = sg.Window(title, layout, icon=image_functions.get_icon())

    while True:
        event, values = ptswindow.read()
        if event in (sg.WINDOW_CLOSED, 'OK. Understood', '-close_popup_text_scroll-'):
            break

    ptswindow.Close()



# Below are program texts
resize_warning_message = '''Something went wrong with resizing. Mostly this is due to missing exif info in your
images or due to incorrect exif info in your images.\n\n
Align_image_stack uses exif data to improve the results. The program will try to continue without it.\n\n
If the align_image_stack preview does not deliver the image you expect, then switch to the
align_imagestack tab and deselect autoHFOV and manually provide a FOV.\n\n
The errors are displayed below:'''

resize_error_message = '''Something went really wrong with resizing.
The program can\'t continue. Please check your images carefully.
You might still try to align_image_stack/enfuse your original images although this will be slower when doing trial and error.'''

about_message = 'About pyEnfuseGUI, Version ' + Version + '\n\n'
about_message += 'pyEnfuseGUI is a graphical frontend for enfuse and align_image_stack.\n'
about_message += 'pyEnfuseGUI is built using Python3 and PySimpleGui.\n\n'
about_message += 'pyEnfuseGUI can be used for exposure bracketing, noise reduction and focus stacking.\n\n'
about_message += 'pyEnfuseGUI is realeased under GPL v3.\n'
about_message += 'Enfuse and Align_image_stack are both released under GPL v2.\n'
about_message += 'You should find both licenses with this software.\n\n'
about_message += 'Author: Harry van der Wolf.'

