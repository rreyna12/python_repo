"""
SUMMARY: Takes exported CSV contact list from KW Command and creates a formatted contact list in CSV format that can
    be used to upload contacts to AMCards and a log file tracking the changes made.

    The only attributes in the formatted contact list are full name, address, birthday and home anniversary.  And the
    list only includes contacts that have:
        - a full name and address
        - either their birthday or home anniversary date
    All other contacts are removed and noted in the log file.

RETURNS:
    - filename_edited.csv: formatted contact list to upload contacts to AMCards, CSV format
    - filename_log.txt: log file with overall summary, filenames, contact counts, and list of formatted and removed
        contacts

NOTES:
    csv module info: https://docs.python.org/3/library/csv.html#module-csv
    logging info: https://docs.python.org/3/library/logging.html

VERSION INFO:
    Created by R. Reyna
    Date: 2024-07-23
    Version: 1.1
    Changes:
        - File names and paths are no longer hardcoded - interact with user to get this information.
        - Fixed some misplaced comments
        - Added very simple implementation of INFO logging, to use must uncomment logging.basicConfig() code
"""
# import modules
import csv
from datetime import datetime  # used in log file
import os
import logging


def get_formatted_datetime():
    """
    Quick function to get the current datetime (datetime.now()) in a
    readable format for the log file.
    datetime.now() returns datetime.datetime(2024, 7, 22, 12, 31, 17, 300828)
    this formats to '22/07/2024 12:31:55'
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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

# log values - these are values collected throughout the script and logged at the very end
num_contacts_orig = 0
num_contacts_formatted = 0
num_contacts_skipped = 0
contacts_formatted = []
contacts_skipped = []

# give user an intro and explain what data is needed
print("--WELCOME TO THE <CONTACT FORMATTING FROM KW COMMAND TO AMCARD> SCRIPT!--")
print("This script will take a CSV contact list exported from KW Command "
      "\nand simplify it to only contacts with an address and either "
      "\nbirthday or home anniversary date.  This list can then be imported "
      "\ninto AMCard, allowing for reminder notifications for that contact's "
      "\nbirthday or home anniversary.")
print("\nPlease provide the information below:")

# STEP 0-A: Get directory to use
print(f"DEFAULT DIRECTORY: {os.getcwd()}")
reqInput = input("- Is the exported contact CSV stored in the default directory above? (y/n): ")

if reqInput.strip().lower() == "y":
    dir_src = os.getcwd()
else:
    retry = True  # in case wrong file path provided
    while retry:
        dir_src = input("- Please provide the file path where the exported contact CSV can be found: ")
        # validate that this file path exists
        dir_src.replace('\\', '/')  # replace w/front slash, win only one uses \ and plan on running this on mac
        if not os.path.exists(dir_src):
            print("ERROR: The file path provided doesn't exist.")
        else:
            retry = False

# STEP 0-B: Get the name of the CSV file
retry = True
while retry:
    filename_orig = input("- What is the file name of the exported CSV?: ")
    # validate that this file exists
    fp = dir_src + "/" + filename_orig
    if not os.path.exists(fp):
        print("ERROR: The file provided doesn't exist.")
    else:
        retry = False

# STEP 0-C: Get the save directory
reqInput = input("- Would you like to save the formatted CSV to the same directory? (y/n): ")
if reqInput.strip().lower() == "y":
    dir_save = dir_src
else:
    retry = True
    while retry:
        dir_save = input("- Where would you like to save the formatted CSV?: ")
        # validate that this file path exists, if not, create it
        dir_save.replace('\\','/')  # replace w/front slash, win only one uses \ and plan on running this on mac
        if not os.path.exists(dir_save):
            reqInput = input("- The directory provided does not exist, would you like to create it? (y/n): ")
            if reqInput.strip().lower() == "y":
                os.mkdir(dir_save)
                print(f"'{dir_save}' created.")
                retry = False
        else:
            retry = False

# STEP 0-i: Now that the input values have been provided, calculate all file names and paths
filename_edited = filename_orig[0:filename_orig.rfind(".")] + "_edited" + filename_orig[filename_orig.rfind("."):]
filename_log = filename_orig[0:filename_orig.rfind(".")] + "_log.txt"
absFilePath_orig = dir_src + '/' + filename_orig
absFilePath_edited = dir_save + '/' + filename_edited
absFilePath_log = dir_save + '/' + filename_log

# logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename=absFilePath_log) # , level=logging.INFO)  # COMMENT OUT 'level' when not testing

print("START: Running text file manipulation script...")
print(f"Original file used: {absFilePath_orig}")
print(f"Edited file produced: {absFilePath_edited}")

with open(absFilePath_log, "w") as f:
    f.write(f"START file conversion process {get_formatted_datetime()}\n")
    f.write(f"Original script: {absFilePath_orig}\n")
    f.write(f"Edited script: {absFilePath_edited}\n")
    f.write(f"---------------------------------------------------------------------------------------------------\n")

# STEP 1: remove the first row - this is a first level category which we want to ignore
with open(absFilePath_orig, "r") as f:
    lines = f.readlines()
with open(absFilePath_orig, "w") as f:
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
with open(absFilePath_edited, 'w') as f:
    f.write(f"{newVal}")

# STEP 3: For each row, determine if they have the requested attributes (see above for complete list).
#   If they do, add them to the edited file, if not, don't do anything
with open(absFilePath_orig, newline='') as csvfile:
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
        with open(absFilePath_edited, 'a') as f:
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
with open(absFilePath_log, "a") as f:
    f.write(f"Total number of original contacts: {num_contacts_orig}\n")
    f.write(f"Number of contacts skipped (see below for list): {num_contacts_skipped}\n")
    f.write(f"Number of contacts formatted (see below for list): {num_contacts_formatted}\n")
    f.write(f"---------------------------------------------------------------------------------------------------\n")
    f.write("--SKIPPED CONTACTS\n")
    f.write(f"{contacts_skipped}\n")
    f.write("--FORMATTED CONTACTS\n")
    f.write(f"{contacts_formatted}\n")
    f.write(f"---------------------------------------------------------------------------------------------------\n")
    f.write(f"END file conversion process {get_formatted_datetime()}\n")
