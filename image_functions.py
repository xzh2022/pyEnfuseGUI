# -*- coding: utf-8 -*-

# image_functions.py
# This helper file does image manipulation and display

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import io, os, math, platform, sys, tempfile
from pathlib import Path
import tkinter as tk
import PySimpleGUI as sg
from PIL import Image # to manipulate images and read exif
import exif  # to read and write exif
from PIL.ExifTags import TAGS
import file_functions

# Use 50 mm as stand for focal length
#fl35mm = 50
import pyenfusegui

image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

# Dictionary holding the translation between tag and tag id
tag_translation = {
    ""
}

def reworkTag(tagtuple, precision):
    value = round (tagtuple[0] / tagtuple[1], precision)
    #print(v[0], ' # ', v[1], ' => ', value)
    return value

def reworkExposure(tagtuple):
    value = "1/" + str(tagtuple[1] // 10)
    return value

# Read all the exif info from the loaded images, if available
def get_all_exif_info(filename):
    exif_dictionary = {}

    img = Image.open(filename)
    exif = img.getexif()
    if exif is not None:
        exif_dictionary['filename'] = img.filename
        exif_dictionary['width x height'] = img.size
        for k, v in img.getexif().items():
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
    else:
        exif_dictionary['no exif'] = 'no exif'

    return exif_dictionary

# Read some basic exif info from a file
def get_basic_exif_info_from_file(filename, output):
    exif_dictionary={}
    correctedfocal = 50

    img=Image.open(filename)
    exifd = img.getexif()
    keys = list(exifd.keys())
    exif_dictionary['filename'] = img.filename
    exif_dictionary['width x height'] = img.size
    for k, v in img.getexif().items():
        if (TAGS.get(k) == 'ISOSpeedRatings'): #ID=0x8827
            #print(TAGS.get(k), " : ", v)
            tag=TAGS.get(k)
            exif_dictionary[tag]=v
        elif (TAGS.get(k) == 'DateTimeOriginal'): # id=0x9003
            #print(TAGS.get(k), " : ", v)
            tag=TAGS.get(k)
            exif_dictionary[tag]=v
        elif (TAGS.get(k) == 'MaxApertureValue'): # ID=0x9205
            #print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)
        elif (TAGS.get(k) == 'FocalLength'): # id=0x920a
            #print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)
        elif (TAGS.get(k)  == 'FocalLengthIn35mmFilm'): # id=0xa405
            #print(TAGS.get(k), " : ", v)
            tag=TAGS.get(k)
            exif_dictionary[tag]=v
            # Field of View (FOV) http://www.bobatkins.com/photography/technical/field_of_view.html
            # FOV(rectilinear) = 2 * arctan(framesize / (focal length * 2)) # framesize 36mm, focal length in 35 mm
            FOV = 2 * (math.atan(36 / (v * 2)))
            exif_dictionary['FOV'] = FOV
        elif (TAGS.get(k) == 'ExposureTime'): # id=0x829a
            #print(TAGS.get(k), " : ", reworkExposure(v))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkExposure(v)
        elif (TAGS.get(k) == 'ExposureBiasValue'): # id=0x9204
            #print("ExposureCompensation\t: ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)
        elif (TAGS.get(k) == 'FNumber'): # id=0x829d
            #print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)


    if (output == 'print'):
        print('\n\n',exif_dictionary)
        #print("\n\n",exif_dictionary['ExposureBiasValue'])

    return exif_dictionary


# This function resizes the original selected images when
# the user clicks on "create preview" or "create enfused image"
def resizetopreview(all_values, folder, tmpfolder):
    img = ""
    failed = ""

    files = all_values['-FILE LIST-']
    for file in files:
        nfile = os.path.join(folder, file)
        #previewfile = os.path.join(tmpfolder, os.path.splitext(file)[0] + ".jpg")
        previewfile = os.path.join(tmpfolder,file)

        if not os.path.exists(previewfile): # This means that the preview file does not exist yet
            print("previewfile: ", previewfile, " does not exist yet")
            if platform.system() == 'Windows':
                img += "\"" + nfile.replace("/", "\\") + "\" "
            else:
                img += "\"" + nfile + "\" "
            try:
                preview_img = Image.open(nfile)
                exifd = preview_img.getexif() # Get all exif data from original image
                sg.user_settings_filename(path=Path.home())
                longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
                preview_img.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
                # Get necessary tags and write them to resized images
                #for k, v in preview_img.getexif().items():
                preview_img.save(previewfile, "JPEG", exif=exifd) # Save all exif data from original to resized image
            except Exception as e:
                failed += pyenfusegui.logger(e) + '\n' # get the error from the logger
                preview_img.save(previewfile, "JPEG")
                #pass
    return failed

def resizesingletopreview(folder, tmpfolder, image):
    img = ""

    previewfile = os.path.join(tmpfolder, image)
    orgfile = os.path.join(folder, image)
    print('previewfile ' + previewfile + '; orgfile ' + orgfile)
    if not os.path.exists(previewfile):  # This means that the preview file does not exist yet
        print("previewfile: ", previewfile, " does not exist yet")
        if platform.system() == 'Windows':
            img += "\"" + orgfile.replace("/", "\\") + "\" "
        else:
            img += "\"" + orgfile + "\" "
        try:
            preview_img = Image.open(orgfile)
            exifd = preview_img.getexif()  # Get all exif data from original image
            sg.user_settings_filename(path=Path.home())
            longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
            preview_img.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
            # Get necessary tags and write them to resized images
            # for k, v in preview_img.getexif().items():
            preview_img.save(previewfile, "JPEG", exif=exifd)  # Save all exif data from original to resized image
        except Exception as e:
            pyenfusegui.logger(e)
            # pass


# This function parses all align_image_stack settings and returns them
# to the create_ais_command
def check_ais_params(all_values):
    cmd_string = ""
    #print('autoCrop ',all_values['_autoCrop_'] )
    if all_values['_autoCrop_']:
        cmd_string += '-C '
    if all_values['_useGPU_']:
        cmd_string += '--gpu  '
    if all_values['_fffImages_']:
        cmd_string += '-e '
    if all_values['_fovOptimize_']:
        cmd_string += '-m '
    if all_values['_optimizeImgCenter_']:
        cmd_string += '-i '
    if all_values['_optimizeRadialDistortion_']:
        cmd_string += '-d '
    if all_values['_linImages_']:
        cmd_string += '-l '
    if not all_values['_autoHfov']:
        cmd_string += '-f ' + all_values['_inHFOV_'] + ' '
    if not all_values['_inNoCP_'] == '8':
        cmd_string += '-c ' + all_values['_inNoCP_'] + ' '
    if not all_values['_removeCPerror_'] == '3':
        cmd_string += '-t ' + all_values['_removeCPerror_'] + ' '
    if not all_values['_inScaleDown_'] == '1':
        cmd_string += '-s ' + all_values['_inScaleDown_'] + ' '
    if not all_values['_inGridsize_'] == '5':
        cmd_string += '-g ' + all_values['_inGridsize_'] + ' '    
        
    return cmd_string

# This function creates the basic align_image)stack command for the several options
# It uses the string from check_ais_params to complete the command string
def create_ais_command(all_values, folder, tmpfolder, type):
    cmd_string = ""
    cmd_list = []

    file_functions.remove_files(os.path.join(tmpfolder,'*ais*'))
    if (type == 'preview'):
        #cmd_string = 'align_image_stack --gpu -a ' + os.path.join(tmpfolder,'preview_ais_001') + ' -v -t 2 -C -i '
        cmd_string = 'align_image_stack --gpu -a ' + os.path.join(tmpfolder, 'preview_ais_001') + ' '
        cmd_list.append('--gpu')
        cmd_list.append('-a')
        cmd_list.append(os.path.join(tmpfolder, 'preview_ais_001'))
    else:
        cmd_string = 'align_image_stack --gpu -a ' + os.path.join(tmpfolder,'ais_001') + ' '
    cmd_string += check_ais_params(all_values)

    files = all_values['-FILE LIST-']
    for file in files:
        if type == 'preview':
            nfile = os.path.join(tmpfolder, file)
        else:
            nfile = os.path.join(folder, file)
        if platform.system() == 'Windows':
            cmd_string += "\"" + nfile.replace("/", "\\") + "\" "
            cmd_list.append("\"" + nfile.replace("/", "\\") + "\" ")
        else:
            cmd_string += "\"" + nfile + "\" "
            cmd_list.append(nfile)
    #print("\n\n", cmd_string, "\n\n")
    return cmd_string

# This function parses all enfuse settings and returns them
# to the create_enfuse_command
def check_enfuse_params(all_values):
    cmd_string = ""
    if not all_values['_levels_'] == '29':
        cmd_string += '--levels=' + str(int(all_values['_levels_'])) + ' '
    if not all_values['_exposure_weight_'] == '1.0':
        cmd_string += '--exposure-weight=' + str(all_values['_exposure_weight_']) + ' '
    if not all_values['_saturation_weight_'] == '0.2':
        cmd_string += '--saturation-weight=' + str(all_values['_saturation_weight_']) + ' '
    if not all_values['_contrast_weight_'] == '0':
        cmd_string += '--contrast-weight=' + str(all_values['_contrast_weight_']) + ' '
    if not all_values['_entropy_weight_'] == '0':
        cmd_string += '--entropy-weight=' + str(all_values['_entropy_weight_']) + ' '
    if not all_values['_exposure_optimum_'] == '0.5':
        cmd_string += '--exposure-optimum=' + str(all_values['_exposure_optimum_']) + ' '
    if not all_values['_exposure_width_'] == '0.2':
        cmd_string += '--exposure-width=' + str(all_values['_exposure_width_']) + ' '
    return cmd_string

def check_enfuse_output_format(all_values):
    cmd_string = ""
    if all_values['_jpg_']:
        if all_values['_jpgCompression_'] == 90:
            cmd_string += '--compression=90 '
        else:
            cmd_string += '--compression=' + str(int(all_values['_jpgCompression_'])) + ' '
    else: # User selected tiff output
        cmd_string += '--compression=' + all_values['_tiffCompression'] + ' --depth='
        if all_values['_tiff8_']:
            cmd_string += '8 '
        elif all_values['_tif16_']:
            cmd_string += '16 '
        else:
            cmd_string += '32 '
    return cmd_string

def create_enfuse_command(all_values, folder, tmpfolder, type, newImageFileName):
    cmd_string = ""
    if type == 'preview_ais':
        cmd_string = 'enfuse -v --compression=90 ' + os.path.join(tmpfolder,'preview_ais_001*') + ' -o ' + os.path.join(tmpfolder,'preview.jpg ')
    elif type == 'preview':
        cmd_string = 'enfuse -v --compression=90 ' + ' -o ' + os.path.join(tmpfolder, 'preview.jpg ')
        files = all_values['-FILE LIST-']
        for file in files:
            nfile = os.path.join(tmpfolder, file)
            if platform.system() == 'Windows':
                cmd_string += "\"" + nfile.replace("/", "\\") + "\" "
            else:
                cmd_string += "\"" + nfile + "\" "
        # print("\n\n", cmd_string, "\n\n")
    elif type == 'full_ais':
        cmd_string = 'enfuse -v ' + os.path.join(tmpfolder,'ais_001*') + ' -o "' + newImageFileName + '" '
        # Check enfuse file output format
        cmd_string += check_enfuse_output_format(all_values)
    else: # full enfuse without ais
        #cmd_string = 'enfuse -v --level=29 --compression=90 ' + ' -o ' + newImageFileName
        cmd_string = 'enfuse -v ' + ' -o "' + newImageFileName + '" '
        # Check enfuse file output format
        cmd_string += check_enfuse_output_format(all_values)
        files = all_values['-FILE LIST-']
        for file in files:
            nfile = os.path.join(folder, file)
            if platform.system() == 'Windows':
                cmd_string += "\"" + nfile.replace("/", "\\") + "\" "
            else:
                cmd_string += "\"" + nfile + "\" "
        # print("\n\n", cmd_string, "\n\n")
    # Finally add our enfuse params
    cmd_string += check_enfuse_params(all_values)

    return cmd_string

def get_curr_screen_geometry():
    """
    Get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]

    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.destroy()
    return geometry
    """
    # Do not use above. It might function better in a multi window environment
    # but shows a gray full screen window for a moment
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy() # do not forget to delete the tk window
    return int(width), int(height)

def display_preview(mainwindow, imgfile):
    try:
        #imgfile = os.path.join(folder, values['-FILE LIST-'][0])
        # image_functions.get_basic_exif_info(imgfile, 'print')
        print("\n\nimgfile ", imgfile)
        image = Image.open(imgfile)
        sg.user_settings_filename(path=Path.home())
        longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
        image.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        mainwindow['-IMAGE-'].update(data=bio.getvalue())
    except:
        # print("Something went wrong converting ", imgfile)
        pass
    #exif_table = image_functions.get_basic_exif_info(imgfile, 'print')

# This displays the final image in the default viewer
def displayImage(imgpath):

    rawimgpath = str(imgpath)
    newImg = Image.open(rawimgpath)
    newImg.show()

def displayImageWindow(imgpath):

    rawimgpath = str(imgpath)
    newImg = Image.open(rawimgpath)
    #imgsize = newImg.size
    scrwidth, scrheight = get_curr_screen_geometry()
    print('scrwidth x scrheight: ' + str(scrwidth) + 'x' + str(scrheight))
    # 4k is 3840 x 2160, HD is 1920 x 18080
    if scrwidth >= 1920 and scrwidth < 3840:
        scrwidth = 1860
        scrheight = 1026
    newImg.thumbnail((scrwidth, scrheight), Image.ANTIALIAS)
    bio = io.BytesIO()
    newImg.save(bio, format='PNG')
    layout = [
        [sg.Image(bio.getvalue(),key='-IMAGE-')],
        [sg.Button('Exit', visible=False, key='-exit-')] # invisible button necessary to allow windows read
    ]
    window = sg.Window('Your image: ' + imgpath, layout, no_titlebar=False, location=(0,0), size=(scrwidth,scrheight), keep_on_top=True, icon=get_icon())

    #window = sg.Window(imgpath, layout,  keep_on_top=True).Finalize()
    #window = sg.Window(imgpath, layout, no_titlebar=False, keep_on_top=True).Finalize().Maximize()
    #window.Maximize()
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED,'-exit-'):
            break
    window.close

# This function adds the program icon to the top-left of the displayed windows and popups
def get_icon():
    if platform.system() == 'Windows':
        wicon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','logo.ico')
    else:
        wicon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','logo.png')

    return wicon