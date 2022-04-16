# -*- coding: utf-8 -*-

# ui_layout.py.py - This python helper scripts holds the user interface functions

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

import io, os, platform
from PIL import Image
from pathlib import Path

import image_functions
import program_texts


#filenames = []
#pathnames = []

def which_folder():
    init_folder = ""
    sg.user_settings_filename(path=Path.home())
    start_folder = sg.user_settings_get_entry('imgfolder', Path.home())
    last_opened_folder = sg.user_settings_get_entry('last_opened_folder', Path.home())
    if last_opened_folder != Path.home():
        init_folder = last_opened_folder
    else:
        init_folder = start_folder

    return init_folder

def display_org_preview(imgfile):
    try:
        print("\n\nimgfile ", imgfile)
        image = Image.open(imgfile)
        sg.user_settings_filename(path=Path.home())
        longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
        image.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        return bio.getvalue()
    except:
        print("Something went wrong converting ", imgfile)
        pass
        return imgfile


#----------------------------------------------------------------------------------------------
#---------------------------------------- Menu ------------------------------------------------
menu_def = [
               ['&File', ['!&Load files', '---', '&Preferences', 'E&xit']],
               ['&Help', ['&About...', 'Align_Image_stack parameters', 'Enfuse parameters']],
           ]

#----------------------------------------------------------------------------------------------
#-------Main function that builds the whole gui and listens tot the commands ------------------
#----------------------------------------------------------------------------------------------
def create_and_show_gui(tmpfolder, startFolder):
# This creates the complete gui and then returns the gui
# to pyenfusegui where the events are evaluated
#----------------------------------------------------------------------------------------------
#---------------- Main tab for the default settings to make an enfused image  -----------------

    layoutMainGeneralCheckBoxes = [
        [sg.Checkbox('Use Align_image_stack', key='_useAIS_', default=True)],
        [sg.Checkbox('Display image after enfusing', key='_dispFinalIMG_', default=True)],
        [sg.Checkbox('Save final image to source folder', key='_saveToSource_', default=True)]
    ]
    layoutMain_SaveAs = [
        [sg.Text('Save Images as:')],
        [sg.Radio('.jpg (Default)', "RADIOSAVEAS", default=True, key='_jpg_'), sg.Spin([x for x in range(1,100)],initial_value="90", key='_jpgCompression_')],
        [sg.Radio('.Tiff 8bits', "RADIOSAVEAS", default=False, key='_tiff8_')],
        [sg.Radio('.Tiff 16 bits', "RADIOSAVEAS", default=False, key='_tiff16_'), sg.Combo(['deflate', 'packbits', 'lzw', 'none'], default_value='deflate', key='_tiffCompression')],
        [sg.Radio('.Tiff 32 bits', "RADIOSAVEAS", default=False, key='_tiff32_')]
    ]
    layoutMain_Presets = [
        [sg.Text('Presets')],
        [sg.Radio('None', "RADIOPRESET", default=True, key='_preset_none_')],
        [sg.Radio('Default (resets all settings to defaults)', "RADIOPRESET", default=False, key='_tiff8_')],
        [sg.Radio('Focus Stacking', "RADIOPRESET", default=False, key='_tiff16_')]
    ]

    layoutMainTab = [
        #[sg.Column(layoutMainGeneralCheckBoxes), sg.VSeperator(), sg.Column(layoutMain_SaveAs), sg.VSeperator(), sg.Column(layoutMain_Presets)]
        [sg.Column(layoutMainGeneralCheckBoxes), sg.VSeperator(), sg.Column(layoutMain_SaveAs),]
    ]
    

#----------------------------------------------------------------------------------------------
#--------------------------- Enfuse tab -----------------
    layoutEnfuseTab_Levels = [
        [sg.Text('Levels')],
        [sg.Slider(key = '_levels_', range=(1,29), resolution='1', default_value='29')]
    ]
    layoutEnfuseTab_ExposureWeight = [
        [sg.Text('Exposure\nweight')],
        [sg.Slider(key = '_exposure_weight_', range=(0,1), resolution='0.1', default_value='1.0')]
    ]
    layoutEnfuseTab_SaturationWeight = [
        [sg.Text('Saturation\nweight')],
        [sg.Slider(key = '_saturation_weight_', range=(0,1), resolution='0.1', default_value='0.2')]
    ]
    layoutEnfuseTab_ContrastWeight = [
        [sg.Text('Contrast\nweight')],
        [sg.Slider(key = '_contrast_weight_', range=(0,1), resolution='0.1', default_value='0')]
    ]
    layoutEnfuseTab_EntropyWeight = [
        [sg.Text('Entropy\nweight')],
        [sg.Slider(key = '_entropy_weight_', range=(0,1), resolution='0.1', default_value='0')]
    ]
    layoutEnfuseTab_ExposureOptimum = [
        [sg.Text('Exposure\noptimum')],
        [sg.Slider(key = '_exposure_optimum_', range=(0,1), resolution='0.1', default_value='0.5')]
    ]

    layoutEnfuseTab_ExposureWidth = [
        [sg.Text('Exposure\nwidth')],
        [sg.Slider(key = '_exposure_width_', range=(0,1), resolution='0.1', default_value='0.2')]
    ]
    layoutEnfuseTab_Mask = [
        [sg.Text('Mask')],
        [sg.Radio('Soft Mask (Default)', "RADIOMASK", default=True, key='_softmask_')],
        [sg.Radio('Hard Mask', "RADIOMASK", default=False, key='_hardmask_')]
    ]
    layoutEnfuseTab_Wrap = [
        [sg.Text('Wrap')],
        [sg.Radio('None (Default)', "RADIOWRAP", default=True, key='_none_')],
        [sg.Radio('Horizontal', "RADIOWRAP", default=False, key='_horizontal_')],
        [sg.Radio('Vertical', "RADIOWRAP", default=False, key='_vertical_')],
        [sg.Radio('Both', "RADIOWRAP", default=False, key='_both_')]
    ]
    layoutEnfuseTab = [
         [sg.Column(layoutEnfuseTab_Levels), sg.Column(layoutEnfuseTab_ExposureWeight), sg.Column(layoutEnfuseTab_SaturationWeight), sg.Column(layoutEnfuseTab_ContrastWeight),
          sg.Column(layoutEnfuseTab_EntropyWeight),sg.Column(layoutEnfuseTab_ExposureOptimum), sg.Column(layoutEnfuseTab_ExposureWidth), sg.VSeperator(),
          sg.Column(layoutEnfuseTab_Mask), sg.Column(layoutEnfuseTab_Wrap)]
    ]

#----------------------------------------------------------------------------------------------
#-------------------------------- Align_image_stack tab --------------------------------
    layoutAIScheckboxes = [
        [sg.Checkbox('Autocrop images', key='_autoCrop_', default=True)],
        [sg.Checkbox('Use GPU for remapping', key='_useGPU_', default=True)],
        [sg.Checkbox('Full Frame Fisheye images', key='_fffImages_', default=False)],
        [sg.Checkbox('Optimize Field of View of all images except first', key='_fovOptimize_', default=False)],
        [sg.Checkbox('Optimize image center of all images except first', key='_optimizeImgCenter_', default=False)],
        [sg.Checkbox('Optimize radial distortion of all images except first', key='_optimizeRadialDistortion_', default=False)],
        [sg.Checkbox('Assume linear input files', key='_linImages_', default=False)],
    ]

    layoutAISInputs = [
        [sg.InputText(key='_inHFOV_', size=(4, 1)), sg.Text("HFOV"), sg.Checkbox('Auto HFOV', key='_autoHfov', default=True)],
        [sg.InputText('8', key='_inNoCP_', size=(4, 1)), sg.Text('No. of Control points')],
        [sg.InputText('3', key='_removeCPerror_', size=(4, 1)), sg.Text('Remove Control points with error > than')],
        [sg.InputText('1', key='_inScaleDown_', size=(4, 1)), sg.Text('Scale down images by 2^ scale')],
        [sg.InputText('5', key='_inGridsize_', size=(4, 1)), sg.Text('Grid size (default: 5x5)')],
    ]

    layoutAISTab = [
        [sg.Column(layoutAIScheckboxes), sg.VSeperator(), sg.Column(layoutAISInputs)]
    ]
#----------------------------------------------------------------------------------------------
#--------------------------- Left and right panel -----------------
    layoutLeftPanel = [
        [sg.In(size=(1, 1), enable_events=True, key="-FILES-", visible=False),
            sg.FilesBrowse(button_text = 'Load Images', font = ('Calibri', 12, 'bold'), initial_folder=which_folder(), file_types = program_texts.image_formats),
            sg.Button('Preferences', font = ('Calibri', 12, 'bold'), key='_btnPreferences_')],
        [sg.Text('Images Folder:')],
        [sg.Text(size=(60, 1), key='-FOLDER-', font = ('Calibri', 10, 'italic'))],
        [sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-")],
        [sg.Checkbox('Display selected image when clicked on', key='_display_selected_')]
    ]

    layoutRightPanel = [
#        [sg.Image(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','preview.png'), key='-IMAGE-')],
        [sg.Image(display_org_preview(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','preview.png')), key='-IMAGE-')],
        [sg.Button('Create Preview', font = ('Calibri', 12, 'bold'), key='_create_preview_'), sg.Checkbox('Use Align_image_stack', key='_useAISPreview_', default=True)]
    ]

#----------------------------------------------------------------------------------------------
#--------------------------- Button Group -----------------
   # layoutButtons = [
   #      [sg.Push(), sg.Button('Create Enfused image', font = ('Calibri', 12, 'bold'), key='_CreateImage_'), sg.Button('Reset all to defaults', font = ('Calibri', 12, 'bold'), key='_ResetAll_'), sg.Button('Close', font = ('Calibri', 12, 'bold'), key = '_Close_')]
   # ]
#----------------------------------------------------------------------------------------------
#--------------------------- Final Window layout -----------------
    layout = [
        [sg.Menu(menu_def, tearoff=False)],
        #[sg.Text("", size=(1,1), key='_tmpfolder_', visible=False)],
        [sg.Column(layoutLeftPanel), sg.VSeperator(), sg.Column(layoutRightPanel)],
        [sg.TabGroup([[sg.Tab('Main', layoutMainTab, tooltip='For default enfuse you can simply stay on this tab'), sg.Tab('Enfuse', layoutEnfuseTab, tooltip='Options to control enfuse outcome'), sg.Tab('Align_image_stack', layoutAISTab)]])],
        #[sg.Frame(layoutButtons)]
        [sg.Push(), sg.Button('Create Enfused image', font = ('Calibri', 12, 'bold'), key='_CreateImage_'), sg.Button('Reset all to defaults', font = ('Calibri', 12, 'bold'), key='_ResetAll_'), sg.Button('Close', font = ('Calibri', 12, 'bold'), key = '_Close_')]
    ]

    # Open the window and return it to pyenfusegui

    #return sg.Window('pyEnfuseGUI ' + program_texts.Version).Layout(layout)
    return sg.Window('pyEnfuseGUI ' + program_texts.Version, layout, icon=image_functions.get_icon())
