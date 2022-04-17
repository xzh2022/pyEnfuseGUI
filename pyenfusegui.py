# -*- coding: utf-8 -*-

# firmware_modder.py - This is the main script to modify the firmware
# for the AllappUpdate.bin

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
import os, sys , tempfile, webbrowser
# Necessary for windows
import requests
from pathlib import Path

#------- Helper python scripts ----
import ui_layout
import Settings
import image_functions
import program_texts
import file_functions
import run_commands


#------- Some constants & variables -----------
sg.theme('SystemDefault1')
sg.SetOptions(font = ('Helvetica', 12))
filenames = []
pathnames = []
image_exif_dictionaries = {}
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

#----------------------------------------------------------------------------------------------
#------------------------------- Helper functions ---------------------------------------------
def replace_strings(Lines, orgstring, newstring):
    newLines = []
    # Now do the replacing
    for line in Lines:
        if orgstring not in line:
            newLines.append(line)
        else:
            newLines.append(newstring + '\n')
    return newLines

"""
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
     +-- Everything else
"""
def logger(e):
    e = sys.exc_info()
    print('Error Return Type: ', type(e))
    print('Error Class: ', e[0])
    print('Error Message: ', e[1])
    return str(e[1])

#----------------------------------------------------------------------------------------------
#----------------------------- Main function --------------------------------------------------
def main():
    tmpfolder = os.path.join(tempfile.gettempdir(), 'pyenfusegui')
    settingsFile = os.path.join(Path.home(), '.pyenfusegui.json')
    file_functions.recreate_tmp_workfolder(tmpfolder)
    sg.user_settings_filename(path=Path.home())
    start_folder = sg.user_settings_get_entry('imgfolder', Path.home())
    print("\n",settingsFile)
    print(tempfile.gettempdir())

    # Display the GUI to the user
    window =  ui_layout.create_and_show_gui(tmpfolder,start_folder)
    while True:
        event, values = window.Read()
        #print('You entered ', values)
        if event == sg.WIN_CLOSED or event == '_Close_' or event == 'Exit':
            file_functions.remove_tmp_workfolder(tmpfolder)
            #print('pressed Close')
            return('Cancel', values)
            break
        elif event == '-FILES-':
            print('values["-FILES-"]   ',values["-FILES-"])
            filenames = []
            window['-FILE LIST-'].update(filenames)
            if values["-FILES-"]: # or values["-FILES-"] == {}: #empty list returns False
                file_list = values["-FILES-"].split(";")
                for file in file_list:
                    # print(f)
                    fname = os.path.basename(file)
                    folder = os.path.dirname(os.path.abspath(file))
                    # Now save this folder as "last opened folder" to our settings
                    sg.user_settings_filename(path=Path.home())
                    sg.user_settings_set_entry('last_opened_folder', folder)
                    filenames.append(fname)
                    pathnames.append(file)
                    # get all exif date if available
                    image_exif_dictionaries[fname] = image_functions.get_all_exif_info(file)
                window['-FILE LIST-'].update(filenames)
                window['-FOLDER-'].update(folder)
        elif event == 'About...':
            window.disappear()
            sg.popup(program_texts.about_message, grab_anywhere=True, keep_on_top=True, icon=image_functions.get_icon())
            window.reappear()
        elif event == 'Align_Image_stack parameters':
            try:
                webbrowser.open('file://' + os.path.join(os.path.realpath(os.getcwd()),'manpages', 'align_image_stack.html') )
                #webbrowser.open('https://manpages.debian.org/testing/hugin-tools/align_image_stack.1.en.html')
            except:
                sg.popup("Can't open the align_image_stack parameters html", icon=image_functions.get_icon())
        elif event == 'Enfuse parameters':
            try:
                webbrowser.open('file://' + os.path.join(os.getcwd(), 'manpages', 'enfuse.html'))
                #webbrowser.open('https://manpages.debian.org/buster/enfuse/enfuse.1.en.html')
            except:
                sg.popup("Can't open the enfuse parameters html", icon=image_functions.get_icon())
        elif event == 'Preferences' or event =='_btnPreferences_':
            Settings.settings_window()
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            #print('A file was chosen from the listbox')
            if values['_display_selected_'] and len(values['-FILE LIST-']) !=0:
                image_functions.resizesingletopreview(folder, tmpfolder, values['-FILE LIST-'][0])
                image_functions.display_preview(window, os.path.join(tmpfolder, values['-FILE LIST-'][0]))
        elif event == '_create_preview_':
            print('pressed Create Preview')
            if len(values['-FILE LIST-']) >1: # We have at least 2 files
                failed = image_functions.resizetopreview(values, folder, tmpfolder)
                go_on = False
                if failed != '':
                    is_zero = file_functions.getFileSizes(values, tmpfolder)
                    if is_zero > 0:
                        #sg.popup_scrolled(program_texts.resize_error_message, failed, icon=image_functions.get_icon())
                        sg.popup(program_texts.resize_error_message, icon=image_functions.get_icon())
                        go_on = False # not necessary but do it anyway
                    else:
                        go_on = True
                        #sg.popup_scrolled(program_texts.resize_warning_message, failed, icon=image_functions.get_icon())
                        program_texts.popup_text_scroll('Something went wrong',program_texts.resize_warning_message, failed)
                if go_on:
                    if (values['_useAISPreview_']):
                        cmdstring = image_functions.create_ais_command(values, folder, tmpfolder, 'preview')
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, "running align_image_stack", False)
                        # print("\n\n" + result + "\n\n")
                        if result == 'OK':
                            cmdstring = image_functions.create_enfuse_command(values, folder, tmpfolder, 'preview_ais','')
                            print("\n\n", cmdstring, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, 'running enfuse', False)
                            image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
                    else:  # Create preview without using ais
                        cmdstring = image_functions.create_enfuse_command(values, folder, tmpfolder, 'preview', '')
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, 'running enfuse', False)
                        image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        elif event == '_CreateImage_':
            print('pressed Create Image')
            if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                if values['_saveToSource_']:
                    folderFileName = file_functions.getFileName(folder)  # user wants to save image to same folder
                else:
                    folderFileName = file_functions.getFileName('')  # user wants to select new folder
                if folderFileName[0] != '' and folderFileName[0] != folder:
                    folder = folderFileName[0]
                if folderFileName[1] == '':
                    sg.popup('Error! no filename provided!', 'You did not provide a filename.\n',
                             'The program can\'t create an image without a filename.', icon=image_functions.get_icon())
                elif folderFileName[1] == 'Cancel':
                    print('user Cancelled')
                else:
                    if values['_useAIS_']:
                        cmdstring = image_functions.create_ais_command(values, folder, tmpfolder, '')
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, '  Now running align_image_stack  \n  Please be patient  ', False)
                        print("\n\n" + result + "\n\n")
                        if result == 'OK':
                            cmdstring = image_functions.create_enfuse_command(values, folder, tmpfolder, 'full_ais',
                                                                              os.path.join(folder, folderFileName[1]))
                            print("\n\n", cmdstring, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, '  Now running enfuse  \n  Please be patient  ', False)
                    else:  # Create full image without using ais
                        cmdstring = image_functions.create_enfuse_command(values, folder, tmpfolder, '',
                                                                          os.path.join(folder, folderFileName[1]))
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, '  Now running enfuse  \n  Please be patient  ', False)
                        # display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
                    if values['_dispFinalIMG_']:
                        #image_functions.displayImage(os.path.join(folder, folderFileName[1]))
                        image_functions.displayImageWindow(os.path.join(folder, folderFileName[1]))
                    #sg.popup("Your created image can be found at:\n\n" + os.path.join(folder, folderFileName[1]) + "\n\n", icon=image_functions.get_icon())
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())

    window.Close()

 
#------------------- Main "boilerplate" function ----------------------------------------------
#----------------------------------------------------------------------------------------------


## Main program, main module
if __name__ == '__main__':
    main()
