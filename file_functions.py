# -*- coding: utf-8 -*-

# file_functions.py - This python helper scripts holds the user interface functions

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import os, tempfile, shutil, glob
import xml.etree.ElementTree as ET

import PySimpleGUI as sg

##################################################################################################
# Configuration xml file
def write_default_config():
    config = "<preferences>\n"
    config += "\t<def_startupfolder></def_startupfolder>\n"
    config += "\t<def_creator></def_creator>\n"
    config += "\t<def_copyright></def_copyright>\n"
    config += "</preferences>\n"

    userpath = os.path.expanduser('~')
    config_filepath = os.path.join(userpath, '.pyenfusegui')
    if not os.path.isdir(config_filepath):
        os.mkdir(config_filepath)
    config_file = open(os.path.join(config_filepath, 'config.xml'), "w")
    config_file.write(config)
    config_file.close()

def error_reading_configparameter(self):
    message = ("Somehow I encountered an error reading the config file.\n"
               "This can happen when:\n"
               "- the config file somehow got damaged.\n"
               "- this is the very first program start.\n\n"
               "pyEnfuseGUI will simply create a new config file. Please "
               "check your preferences.")
    #window.disappear()
    sg.popup(message)
    #window.reappear()

def read_xml_config(self):
    tempstr = lambda val: '' if val is None else val

    userpath = os.path.expanduser('~')
    #print(userpath)
    print("reading from " + os.path.join(userpath, '.pyenfusegui', 'config.xml'))
    # First we check in the safe way for the existence of the config file
    if os.path.isfile(os.path.join(userpath, '.pyenfusegui', 'config.xml')):
        try:
            self.configtree = ET.parse(os.path.join(userpath, '.pyenfusegui', 'config.xml'))
            self.configroot = self.configtree.getroot()
        except:
            sg.popup("Error!", "config.xml exists, but unable to open config.xml" )
            file_read = False
    else: # No lensdb.xml => first time use or whatever error
        error_reading_configparameter(self)
        write_default_config()
        self.configtree = ET.parse(os.path.join(userpath, '.pyenfusegui', 'config.xml'))
        self.configroot = self.configtree.getroot()

    for pref_record in self.configroot:
        for tags in pref_record.iter('alternate_exiftool'):
            if tags.text == "True":
                self.alternate_exiftool = True
            else:
                self.alternate_exiftool = False
        for tags in pref_record.iter('exiftooloption'):
            self.exiftooloption.setText(tags.text)
        for tags in pref_record.iter('pref_thumbnail_preview'):
            if tags.text == "True":
                self.pref_thumbnail_preview.setChecked(1)
            else:
                self.pref_thumbnail_preview.setChecked(0)
        for tags in pref_record.iter('def_startupfolder'):
            self.LineEdit_def_startupfolder.setText(tags.text)
        for tags in pref_record.iter('def_creator'):
            self.def_creator.setText(tags.text)
        for tags in pref_record.iter('def_copyright'):
            self.def_copyright.setText(tags.text)
        for tags in pref_record.iter('images_view'):
            print(tags.text)
            index = self.images_view.findText(tags.text, Qt.MatchFixedString)
            if index >= 0:
                self.images_view.setCurrentIndex(index)
        

def write_xml_config(self):
    for pref_record in self.configroot:
        for tags in pref_record.iter('alternate_exiftool'):
            if self.exiftooloption.text() == "":
                tags.text = "False"
                self.alternate_exiftool = False
            else:
                tags.text = "True"
                self.alternate_exiftool = True
        for tags in pref_record.iter('exiftooloption'):
            tags.text = self.exiftooloption.text()
        for tags in pref_record.iter('pref_thumbnail_preview'):
            if self.pref_thumbnail_preview.isChecked():
                tags.text = "True"
            else:
                tags.text = "False"
        for tags in pref_record.iter('def_startupfolder'):
            tags.text = self.LineEdit_def_startupfolder.text()
        for tags in pref_record.iter('def_creator'):
            tags.text = self.def_creator.text()
        for tags in pref_record.iter('def_copyright'):
            tags.text = self.def_copyright.text()
        for tags in pref_record.iter('images_view'):
            tags.text = self.images_view.currentText()

    try:
        userpath = os.path.expanduser('~')
        #print(userpath)
        self.configtree.write(os.path.join(userpath, '.pyenfusegui', 'config.xml'))
    except:
        sg.popup("Error!", "Unable to open config.xml for writing" )


# End of Configuration xml file
##################################################################################################
# This functions (re)creates our work folder which is a subfolder
# of the platform define tmp folder
def recreate_tmp_workfolder(tmp_folder):
    #tmp_folder = os.path.join(tempfile.gettempdir(), 'jimgfuse')
    if os.path.exists(tmp_folder):
        try:
            shutil.rmtree(tmp_folder) # emove all contents of the folder
        except:
            print('Error deleting directory')
        # Now leave it be as it is now empty
    else: # It does not exist so we need to recreate it
        os.mkdir(tmp_folder)

def remove_tmp_workfolder(tmp_folder):

    if os.path.exists(tmp_folder):
        try:
            shutil.rmtree(tmp_folder) # emove folder with all contents
        except:
            print('Error deleting directory')

def remove_files(filepattern):
    fileList = glob.glob(filepattern)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
            

def readFile(filename):
    # read the file using readlines
    orgFile = open(filename, 'r', encoding='utf-8')
    Lines = orgFile.readlines()
    orgFile.close()
    return Lines

def writeFile(filename, Lines):
    newFile = open(filename, 'w', encoding='utf-8')
    newFile.writelines(Lines)
    newFile.close()

def getFileName(folder):
    fileName = ""
    foldertxt = ""
    folderInputTxt = ""
    if folder == '':
        foldertxt = 'Select a folder for your output image'
    else:
        foldertxt = 'You selected the images source folder as destination.\nClick "Browse" to select another folder'
        folderInputTxt = folder

    layout = [[sg.Text('Enter a filename without extension:')],
              [sg.Input(key='-FILENAME-')],
              [sg.Text(foldertxt)],
              [sg.Input(folderInputTxt, key='-FOLDER-'), sg.FolderBrowse()],
              [sg.B('OK'), sg.B('Cancel')]]

    window = sg.Window('Provide a filename', layout)
    while True:
        event, values = window.read()
        if event in(sg.WINDOW_CLOSED, 'Cancel'):
            folder = ''
            fileName = 'Cancel'
            break
        elif event == 'OK':
            fileName= values['-FILENAME-']
            folder = values['-FOLDER-']
            break

    window.close()
    return folder, fileName