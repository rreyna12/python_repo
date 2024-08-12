"""
SUMMARY: Takes exported CSV contact list from KW Command and creates a formatted contact list in CSV format that can
    be used to upload contacts to AMCards and a log file tracking the changes made.

    The only attributes in the formatted contact list are full name, address, birthday and home anniversary.  And the
    list only includes contacts that have:
        - a full name and address
        - either their birthday or home anniversary date
    All other contacts are removed and noted in the log file.

    **KW Command does have home and mailing addresses, unfortunately the column headers are exactly the same for both,
    (Address line 1, Address line 2, etc).  By default, the program does provide the mailing address in the formatted
    file.

RETURNS:
    - filename_edited.csv: formatted contact list to upload contacts to AMCards, CSV format
    - filename_log.txt: log file with overall summary, filenames, contact counts, and list of formatted and removed
        contacts

NOTES:
    csv module info: https://docs.python.org/3/library/csv.html#module-csv
    logging info: https://docs.python.org/3/library/logging.html
    TkInter info (forms): https://wiki.python.org/moin/TkInter
    ttk into (Tk themed widgets): https://docs.python.org/3/library/tkinter.ttk.html
    fonts: https://www.geeksforgeeks.org/underline-text-in-tkinter-label-widget/
    https://python-course.eu/tkinter/radio-buttons-in-tkinter.php

VERSION INFO:
    Created by R. Reyna
    Date: 2024-07-23
    Version: 1.2
    Changes:
        - Validated mailing address is used and not home; updated summary
        - Implementing first step of having a form vs having to use the command line/prompt
            - This is a basic implementation of a form, will improve form and code organization in next update

    Future Change:
        - fix bug and loop radio button creation (see TODO s below)
"""
# import modules
import csv
import tkinter
from datetime import datetime  # used in log file
import os
import logging
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
# https://stackoverflow.com/questions/74901265/set-label-font-to-bold-without-changing-its-size-and-its-font
from tkinter import font as tkfont


class FileData:
    """Class that stores all relevant file and folder path info; in this case only absolute file paths are needed"""
    def __init__(self, filepathabs_csv_orig: str, filepathabs_csv_edited: str, filepathabs_txt_log: str):
        self.absFilePath_csv_orig = filepathabs_csv_orig
        self.absFilePath_csv_edited = filepathabs_csv_edited
        self.absFilePath_txt_log = filepathabs_txt_log


def calc_file_names_and_paths(dir_save: str, csv_filepathabs: str):
    """Using the provided save dir and csv file name, determine the edited file name and absolute file paths to use
    :param dir_save: the chosen directory where new files will be saved
    :param csv_filepathabs: absolute file path of the csv file to be edited
    :return: a FileData object
    """

    try:
        if not dir_save:
            raise ValueError("Save directory not selected", "dir_save")
            # raise Exception("(exception) Save directory not selected")
        if not csv_filepathabs:
            raise ValueError("CSV file not selected", "csv_filepathabs")
            # raise Exception("(exception) CSV file not selected")

        # replace w/front slash, win only one to use \ and plan on running this on mac
        if dir_save.find("\\"):
            dir_save = dir_save.replace('\\', '/')
        if csv_filepathabs.find("\\"):
            csv_filepathabs = csv_filepathabs.replace('\\', '/')

        # strip csv file name and source directory from csv_filepathabs
        dir_src = csv_filepathabs[:(csv_filepathabs.rfind("/"))]  # source directory
        filename_orig = csv_filepathabs[(csv_filepathabs.rfind("/") + 1):]  # csv original file name
        # STEP 0-i: Now that the input values have been provided, calculate all file names and paths
        filename_edited = filename_orig[0:filename_orig.rfind(".")] + "_edited" + filename_orig[filename_orig.rfind("."):]
        filename_log = filename_orig[0:filename_orig.rfind(".")] + "_log.txt"

        fd = FileData
        fd.absFilePath_csv_orig = dir_src + '/' + filename_orig
        fd.absFilePath_csv_edited = dir_save + '/' + filename_edited
        fd.absFilePath_txt_log = dir_save + '/' + filename_log

        return fd

    # TODO: right now this only warns via GUI, update so that it updates the log file as well
    except ValueError as err:  # variables are empty, throw up warning window for user
        if err.args.__contains__("dir_save"):  # missing save directory
            err_msg_calc = "Save directory is unselected, please pick one from the previous screen."
        if err.args.__contains__("csv_filepathabs"):  # missing CSV absolute file path and name
            err_msg_calc = "CSV file is unselected, please pick one from the previous screen."

    # build warning form
    rootWindow_warn_calc = Tk()
    rootWindow_warn_calc.title("WARNING: Missing values")
    rootWindow_warn_calc.eval('tk::PlaceWindow . center')  # centers the form in the middle of the screen

    # build main form
    frm_main_warn_calc = ttk.Frame(rootWindow_warn_calc, padding=pad_fm_lb)
    # --main (warning): intro message (label)
    obj_warn_calc_lb_intro = ttk.Label(frm_main_warn_calc, text=err_msg_calc)
    # --main (warning): OK/close (button)
    obj_warn_calc_button_quit = ttk.Button(frm_main_warn_calc, text="OK", command=rootWindow_warn_calc.destroy)

    # --GRID ITEMS
    frm_main_warn_calc.grid()
    # in frm_main_warn
    obj_warn_calc_lb_intro.grid(column=0, row=0)
    obj_warn_calc_button_quit.grid(column=0, row=1)


def display_format_results(filepathasb_csv_orig: str, filepathabs_csv_edited: str, filepathabs_txt_log: str,
                           result_passfail: bool, fail_msg: str = ""):
    """
    Will display to the user the results of the formatting in a tkinter GUI form.
    If success, let the user know it was successful and where the files can be found.
    If fail, will let the user know that there was an error and why.

    :param filepathabs_csv_orig: absolute file path of the original csv file (already exists)
    :param filepathabs_csv_edited: absolute file path of the edited csv file (should have been created)
    :param filepathabs_txt_log: absolute file path of the log txt file (should have been created)
    :param result_passfail: status of if the process passed or failed. Pass = True (1), Fail = False (0)
    :param fail_msg: an optional message with additional details of the failure to be displayed
    """

    if result_passfail == True:  # success
        title_result = "SUCCESS"
        msg_result = "The process was successful, see list of files below for the formatted file and log file."

    elif result_passfail == False: # fail
        title_result = "FAIL"
        msg_result = "The process failed, please see log file below for more details.  Running program in test mode"

        if fail_msg:
            msg_result += f"\n\nERROR DETAILS: {fail_msg}"

    # build warning form
    rootWindow_result = Tk()
    rootWindow_result.title(title_result)
    rootWindow_result.eval('tk::PlaceWindow . center')  # centers the form in the middle of the screen

    # build main form
    frm_main_result = ttk.Frame(rootWindow_result, padding=pad_fm_lb)
    # --main (frame)
    obj_lf_result = ttk.LabelFrame(frm_main_result, padding=pad_fm_lb)
    obj_lf_result.configure({"relief": "flat"})  # hide default indented frame outline  # TODO, DOESN'T SEEM TO WORK
    # --main (result): message (label)
    obj_result_lb_msg = ttk.Label(obj_lf_result, text=msg_result)
    # --main (result) spacer (label); puts blank space between result msg and file info
    obj_result_lb_spacer = ttk.Label(obj_lf_result, text="", padding=pad_ln_space)
    # --main (result): files (label) // only include CSV orig and edited if successful, always include log
    if result_passfail == True:
        obj_result_lb_msg_csv_orig_header = ttk.Label(obj_lf_result, text="Original File", font=font_reg_bold)
        obj_result_lb_msg_csv_orig_val = ttk.Label(obj_lf_result, text=filepathasb_csv_orig)
        obj_result_lb_msg_csv_edit_header = ttk.Label(obj_lf_result, text="Formatted File", font=font_reg_bold)
        obj_result_lb_msg_csv_edit_val = ttk.Label(obj_lf_result, text=filepathabs_csv_edited)
    obj_result_lb_msg_log_header = ttk.Label(obj_lf_result, text="Log File", font=font_reg_bold)
    obj_result_lb_msg_log_val = ttk.Label(obj_lf_result, text=filepathabs_txt_log)

    # --main (result): OK/close (button)
    obj_result_button_quit = ttk.Button(frm_main_result, text="Close Program"
                                      #, command={rootWindow.destroy, rootWindow_result.destroy})  # TODO: update to close both windows
                                      , command=rootWindow_result.destroy)

    # --GRID ITEMS
    frm_main_result.grid()
    obj_lf_result.grid(column=0, row=0, sticky=W)
    # in frm_main_result
    obj_result_lb_msg.grid(column=0, row=0, columnspan=3, sticky=W)
    obj_result_lb_spacer.grid(column=0, row=1)
    if result_passfail == True:
        obj_result_lb_msg_csv_orig_header.grid(column=0, row=3, sticky=W)
        obj_result_lb_msg_csv_orig_val.grid(column=1, row=3, sticky=W)
        obj_result_lb_msg_csv_edit_header.grid(column=0, row=4, sticky=W)
        obj_result_lb_msg_csv_edit_val.grid(column=1, row=4, sticky=W)
    obj_result_lb_msg_log_header.grid(column=0, row=5, sticky=W)
    obj_result_lb_msg_log_val.grid(column=1, row=5, sticky=W)
    obj_result_button_quit.grid(column=0, row=1)


def exec_format_csv_file(dir_save: str, csv_filepathabs: str, run_testmode: bool = False):
    """
    :param dir_save: the directory where all new files will be saved
    :param csv_filepathabs: absolute file path of the csv file to be formatted
    Executes the full process for formatting the csv file, calling calc_file_names_and_paths,
    format_csv_file and display_format_results
    """

    # calc the file names and paths
    file_data = calc_file_names_and_paths(dir_save, csv_filepathabs)

    # format the file
    result = format_csv_file(filepathabs_csv_orig=file_data.absFilePath_csv_orig
                                , filepathabs_csv_edited=file_data.absFilePath_csv_edited
                                , filepathabs_txt_log=file_data.absFilePath_txt_log
                                , run_testmode=run_testmode)

    display_format_results(filepathasb_csv_orig=file_data.absFilePath_csv_orig
                           , filepathabs_csv_edited=file_data.absFilePath_csv_edited
                           , filepathabs_txt_log=file_data.absFilePath_txt_log, result_passfail=result)


def format_csv_file(filepathabs_csv_orig, filepathabs_csv_edited, filepathabs_txt_log, run_testmode: bool = False):
    """
    Formats the provided csv file, outputting an edited file and log file.  **Requires information from
    calc_file_names_and_paths**.  Called as part of the exec_format_csv_file function

    :param filepathabs_csv_orig: absolute file path of the original csv file (already exists)
    :param filepathabs_csv_edited: absolute file path of the edited csv file (will be created)
    :param filepathabs_txt_log: absolute file path of the log txt file (will be created)
    :param run_testmode: allows the user to run the logger in test mode and provide additional info for troubleshooting
    :return: True/False for the result of the formatting (True = success, False = Fail)
    """

    try:
        # log values - these are values collected throughout the function and logged at the very end
        num_contacts_orig = 0
        num_contacts_formatted = 0
        num_contacts_skipped = 0
        contacts_formatted = []
        contacts_skipped = []

        # logging
        logger = logging.getLogger(__name__)

        if run_testmode:
            logging.basicConfig(filename=filepathabs_txt_log, level=logging.INFO)
        else:
            logging.basicConfig(filename=filepathabs_txt_log)

        print("START: Running text file manipulation script...")
        print(f"Original file used: {filepathabs_csv_orig}")
        print(f"Edited file produced: {filepathabs_csv_edited}")

        with open(filepathabs_txt_log, "w") as f:
            f.write(f"START file conversion process {get_formatted_datetime()}\n")
            f.write(f"Original script: {filepathabs_csv_orig}\n")
            f.write(f"Edited script: {filepathabs_csv_edited}\n")
            f.write(
                f"---------------------------------------------------------------------------------------------------\n")

        # STEP 1: remove the first row - this is a first level category which we want to ignore
        with open(filepathabs_csv_orig, "r") as f:
            lines = f.readlines()
        with open(filepathabs_csv_orig, "w") as f:
            for line in lines:
                if not ("Key Dates") in line and not ("Select Y if applies") in line:
                    f.write(line)

        # STEP 2: add the first row (header) to the edited file
        newVal = ''
        for attr in attrdict:
            if newVal:
                newVal += "," + attr
            else:  # first value, don't include comma
                newVal = attr
        with open(filepathabs_csv_edited, 'w') as f:
            f.write(f"{newVal}")

        # STEP 3: For each row, determine if they have the requested attributes (see above for complete list).
        #   If they do, add them to the edited file, if not, don't do anything
        with open(filepathabs_csv_orig, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                num_contacts_orig += 1  # work on getting total of original contacts

                # check to see if all the required attributes (attrdict) have values
                formatBOOL = True  # start true, will fail if any of the required attrs are missing
                # check the absolutely required attributes first
                for attr in attrdict_required:
                    if not row[attr]:
                        formatBOOL = False
                        logger.info(f"SKIPPING CONTACT: Missing {attr} - {row}")

                if formatBOOL:  # has all the req attributes, continue to 'either or' - only one is needed
                    checkDateBOOL = False  # start false, will turn true if any of the 'either or' attrs are found
                    for attr in attrdict_eitherOr:
                        if row[attr]:
                            checkDateBOOL = True
                            logger.info(f"FORMATTING CONTACT: At least one date found ({attr}) - {row}")

                    if not checkDateBOOL:
                        formatBOOL = False
                        logger.info(f"SKIPPING CONTACT: No dates found - {row}")

                # write the csv values to the new file
                with open(filepathabs_csv_edited, 'a') as f:
                    if formatBOOL:
                        # format and write new contact to edited file and increase log values
                        newVal = ''
                        for attr in attrdict:
                            if newVal:
                                newVal += "," + row[attr]
                            else:  # first value, don't include comma
                                newVal = row[attr]
                        f.write(f"\n{newVal}")

                        # update log values
                        contacts_formatted.append(f"{row[attr_firstname]} {row[attr_lastname]}")
                        num_contacts_formatted += 1

                    else:
                        # update log values
                        contacts_skipped.append(f"{row[attr_firstname]} {row[attr_lastname]}")
                        num_contacts_skipped += 1

        # STEP 4: update log file with results
        with open(filepathabs_txt_log, "a") as f:
            f.write(f"Total number of original contacts: {num_contacts_orig}\n")
            f.write(f"Number of contacts skipped (see below for list): {num_contacts_skipped}\n")
            f.write(f"Number of contacts formatted (see below for list): {num_contacts_formatted}\n")
            f.write(
                f"---------------------------------------------------------------------------------------------------\n")
            f.write("--SKIPPED CONTACTS\n")
            f.write(f"{contacts_skipped}\n")
            f.write("--FORMATTED CONTACTS\n")
            f.write(f"{contacts_formatted}\n")
            f.write(
                f"---------------------------------------------------------------------------------------------------\n")
            f.write(f"END file conversion process {get_formatted_datetime()}\n")

        return True

    except:
        return False


def get_formatted_datetime():
    """
    Quick function to get the current datetime (datetime.now()) in a
    readable format for the log file.
    datetime.now() returns datetime.datetime(2024, 7, 22, 12, 31, 17, 300828)
    this formats to '22/07/2024 12:31:55'
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def get_dir_curr():
    """Get the current directory file path"""
    return os.getcwd()


def get_dir_specific():
    """Get a specific directory path from the user
    source: https://www.tutorialspoint.com/how-to-select-a-directory-and-store-the-location-using-tkinter-in-python
    source: https://docs.python.org/3/library/dialog.html
    """
    return filedialog.askdirectory(mustexist=True)


def get_file_csv():
    """Allow user to select a specific csv file, used to pick the CSV file to format
    source: https://docs.python.org/3/library/dialog.html
    """
    return filedialog.askopenfile(defaultextension='.csv', filetypes=[('CSV files', '*.csv')]
                                  , initialdir=get_dir_curr())


def set_dir_default(lb_to_set: ttk.Label):
    """Changes value of a ttk label to default dir"""
    lb_to_set.config(text=get_dir_curr())


def set_dir_specific(lb_to_set: ttk.Label):
    """Changes value of a ttk label to selected dir"""
    lb_to_set.config(text=get_dir_specific())


def set_file_csv(lb_to_set: ttk.Label):
    """Changes value of a ttk label to selected file csv"""
    lb_to_set.config(text=get_file_csv().name)


if __name__ == "__main__":
    # attribute names
    attr_firstname = "First Name"
    attr_lastname = "Last Name"
    attr_birthday = "Birthday"
    attr_anniversary = "Home Anniversary"
    attr_address1 = "Address line 1"
    attr_address2 = "Address line 2"  # not required, this is usually something like 'Unit 3'
    attr_city = "City"
    attr_state = "State"
    attr_country = "Country"
    attr_zip = "Zip code"
    attrdict = (attr_firstname, attr_lastname, attr_birthday, attr_anniversary,
                attr_address1, attr_address2, attr_city, attr_state,
                attr_zip, attr_country)
    attrdict_required = (attr_firstname, attr_lastname, attr_address1,
                         attr_city, attr_state, attr_zip, attr_country)  # these are required to matter what
    attrdict_eitherOr = (attr_birthday, attr_anniversary)  # contacts need AT LEAST one of these, but don't need both

    # user messages - these are messages that are presented to the user
    msg_title = "CONTACT FORMATTING (KW > AMCARD)"
    msg_script_summary = ("This script will take a CSV contact list exported from KW Command "
                          "\nand simplify it to only contacts with an address and either"
                          "\nbirthday or home anniversary date.  This list can then be imported "
                          "\ninto AMCard, allowing for reminder notifications for that contact's "
                          "\nbirthday or home anniversary."
                          "\n\nPlease provide the required information below:\n")

    # open form
    # --SET FORM DEFAULTS
    pad_fm_lb = 8
    pad_ln_space_header = 5
    pad_ln_space = 1
    pad_rbutton_outerx = 5
    pad_rbutton_outery = 5
    pad_rbutton_innerx = 5
    pad_rbutton_innery = 2
    # fonts have to be built after Tk(), so they can be found below

    # --CREATE FORM ITEMS
    # give user an intro and explain what data is needed
    rootWindow = Tk()
    rootWindow.title(msg_title)
    # create fonts; this has to come after Tk()
    font_reg = tkfont.Font(family="Segeo UI", size=9, weight='bold', slant='roman'
                           , underline=False, overstrike=False)
    font_reg_bold = tkfont.Font(family="Segeo UI", size=9, weight='bold', slant='roman'
                                , underline=False, overstrike=False)
    font_header = tkfont.Font(family="Segeo UI", size=12, weight='bold', slant='roman'
                              , underline=True, overstrike=False)
    font_footnote = tkfont.Font(family="Segeo UI", size=8, weight='normal', slant='italic'
                           , underline=False, overstrike=False)

    # build main form
    frm_main = ttk.Frame(rootWindow, padding=pad_fm_lb)
    # --main: intro message (frame)
    obj_lf_intro = ttk.LabelFrame(frm_main, padding=pad_fm_lb)
    obj_lf_intro.configure({"relief": "flat"})  # hide default indented frame outline  # TODO, DOESN'T SEEM TO WORK
    # --main: intro message (label)
    obj_lb_intro_summary = ttk.Label(obj_lf_intro, text=msg_script_summary)
    # --main: spacer (label); puts space between req info and continue/quit buttons
    obj_lb_spacer1 = ttk.Label(frm_main, text="", padding=pad_ln_space)
    # --main: run in test mode (checkbox)
    var_cb_testMode = IntVar()
    obj_cb_testMode = tkinter.Checkbutton(frm_main, text="Run in test mode", variable=var_cb_testMode, onvalue=1
                                          , offvalue=0, height=2, width=15, font=font_footnote)
    obj_cb_testMode.config(bg="#d44c4c", fg="#0a0000")
    # --main: continue/format file (button)
    # TODO: want to add some sort of check to make sure that the 'csv' file is selected; maybe don't let this be clicked until that value exists?
    obj_button_cont = ttk.Button(frm_main, text="Continue"
                                 , command=lambda: exec_format_csv_file(dir_save=obj_lb_dirToUse_val.cget('text')
                                                                        , csv_filepathabs=obj_lb_cvsFile_val.cget('text')
                                                                        , run_testmode=var_cb_testMode.get()))
    # --main: quit (button)
    obj_button_quit = ttk.Button(frm_main, text="Quit", command=rootWindow.destroy)
    # --req info (frame)
    obj_lf_reqInfo = ttk.LabelFrame(frm_main, padding=pad_fm_lb)
    obj_lb_reqInfo_title = ttk.Label(obj_lf_reqInfo, text="REQUIRED INFORMATION", padding=pad_ln_space_header,
                                     font=font_header)

    # --req info: default save directory (label)
    obj_lb_dirDefault = tkinter.Label(obj_lf_reqInfo, text="Default save directory: ", font=font_reg_bold)
    obj_lb_dirDefault_val = ttk.Label(obj_lf_reqInfo, text=f"{get_dir_curr()}", padding=pad_ln_space)
    # --req info: spacer (label); puts space between default val and changeable vals
    obj_lb_spacer2 = ttk.Label(obj_lf_reqInfo, text="", padding=pad_ln_space)
    # --req info: CSV file to format (label)
    obj_lb_csvFile = tkinter.Label(obj_lf_reqInfo, text="CSV file to format: ", font=font_reg_bold)
    obj_lb_cvsFile_val = ttk.Label(obj_lf_reqInfo, text="", padding=pad_ln_space)
    # --req info: button to select CSV file to format (button)
    obj_button_csvFileSelect = ttk.Button(obj_lf_reqInfo, text="select", command=lambda: set_file_csv(obj_lb_cvsFile_val))
    # --req info: directory used (label)
    obj_lb_dirToUse = ttk.Label(obj_lf_reqInfo, text="Save directory: ", font=font_reg_bold)
    obj_lb_dirToUse_val = ttk.Label(obj_lf_reqInfo, text=f"{get_dir_curr()}", padding=pad_ln_space)

    # TODO: improve by looping radio button creation, see commented out notes below
    # --req info: radio button for using default directory or one below
    obj_lf_reqInfo_buttons = tkinter.LabelFrame(obj_lf_reqInfo)
    obj_lf_reqInfo_buttons.configure({"relief": "flat"})  # hide default indented frame outline
    var_rb = IntVar()
    var_rb.set(100)  # initializing the default choice, default directory

    cmd1 = "set_dir_default(obj_lb_dirToUse_val)"
    cmd2 = "set_dir_specific(obj_lb_dirToUse_val)"
    button1 = tkinter.Radiobutton(obj_lf_reqInfo_buttons, text="Use default directory", variable=var_rb, value=100
                                  , indicator=0, backgroun="#abb0b3", selectcolor="#68abd4"
                                  , command=lambda: exec(cmd1))
    button1.pack(side="left", anchor="w", padx=pad_rbutton_outerx, pady=pad_rbutton_outery
                 , ipadx=pad_rbutton_innerx, ipady=pad_rbutton_innery)
    button2 = tkinter.Radiobutton(obj_lf_reqInfo_buttons, text="Select directory", variable=var_rb, value=200
                                  , indicator=0, backgroun="#abb0b3", selectcolor="#68abd4"
                                  , command=lambda: exec(cmd2))
    button2.pack(side="left", anchor="w", padx=pad_rbutton_outerx, pady=pad_rbutton_outery
                 , ipadx=pad_rbutton_innerx, ipady=pad_rbutton_innery)

    """
    # TODO: improve by looping radio button creation. Current issue, values do loop correctly, but for some reason
    #  the very last command provided gets applied to ALL of the buttons
    # options: [display text, justify (text alignment), variable assigned, column (grid), row (grid), command]
    options = [("Use default directory", "left", 100, 1, 3, "set_dir_default(obj_lb_dirToUse_val)"),
               ("Select directory", "left", 200, 10, 3, "get_dir_specific(obj_lb_dirToUse_val)")]

    for text, justify, val, gridCol, gridRow, cmd in options:
        # indicator on makes a button vs radio / w/out lambda sub-process, command is immediately exec
        button = tkinter.Radiobutton(obj_lf_reqInfo_buttons, text=text, variable=var_rb, value=val
                                     , indicator=0, backgroun="#abb0b3", selectcolor="#68abd4"
                                     , command=lambda: exec(cmd))
        button.pack(side="left", anchor="w", padx=5, pady=2, ipadx=5, ipady=2)
    """

    # --GRID FORM ITEMS
    frm_main.grid()
    # in frm_main
    obj_lf_intro.grid(column=0, row=0, columnspan=6, sticky=W)
    obj_lf_reqInfo.grid(column=0, row=1, columnspan=6)
    # leave row 3 blank; space before run in test mode
    obj_lb_spacer1.grid(column=0, row=2)
    obj_cb_testMode.grid(column=5, row=3, columnspan=2, sticky=E)
    obj_button_cont.grid(column=5, row=4, sticky=E)
    obj_button_quit.grid(column=6, row=4, sticky=W)
    # in obj_lf_intro
    obj_lb_intro_summary.grid(column=0, row=0, columnspan=5, sticky=W)  # sticky=W aligns left
    # in obj_lf_reqInfo
    obj_lb_reqInfo_title.grid(column=0, row=1, columnspan=5)
    # --obj_lf_reqInfo: Default save directory
    obj_lb_dirDefault.grid(column=0, row=2, sticky=W)
    obj_lb_dirDefault_val.grid(column=2, row=2, columnspan=2, sticky=W)  # need columnspan to accommodate CSV button
    # --obj_lf_reqInfo: leave row 3 blank
    obj_lb_spacer2.grid(column=0, row=3)
    # --obj_lf_reqInfo: CSV file to format
    obj_lb_csvFile.grid(column=0, row=4, sticky=W)
    obj_button_csvFileSelect.grid(column=2, row=4, sticky=W)
    obj_lb_cvsFile_val.grid(column=3, row=4, columnspan=2, sticky=W)  # need columnspan to accommodate CSV button
    # --obj_lf_reqInfo: Save directory
    obj_lb_dirToUse.grid(column=0, row=5, sticky=W)
    obj_lb_dirToUse_val.grid(column=2, row=5, columnspan=2, sticky=W)
    # in obj_lf_reqInfo_buttons
    # --obj_lf_reqInfo: buttons use default directory / select directory
    obj_lf_reqInfo_buttons.grid(column=2, row=10, columnspan=2, sticky=W)  # need columnspan to accommodate CSV button
    # TODO: figure way to calc the row value here instead of just setting to high num, enumerate()

    # get the save directory value
    print("test stop 1")  # TODO: delete test
    print(f"dir to use: {obj_lb_dirToUse_val.cget('text')}")
    print(f"CSV file (abs filepath): {obj_lb_cvsFile_val.cget('text')}")
    print(f"Run as text checkbox: {var_cb_testMode.get()}")

    # Start the GUI
    rootWindow.mainloop()  # needs to be at the end; essentially causes a break, allowing form to be graphed
