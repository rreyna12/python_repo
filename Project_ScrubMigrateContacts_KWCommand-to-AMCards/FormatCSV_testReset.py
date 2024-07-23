"""
SUMMARY:
    To be used in conjunction with FormatCSV.py.  Resets my testing environment.
Requires the following files:
  - .testFiles/testDoc_template.csv
Resets the test environment, which for now means it:
  - deletes the test document (testDoc.csv)
  - deletes any edited documents (testDoc_edited.csv)
  - deletes any log files (testDoc_log.csv)
  - creates a new version of the test document (copies and renamed testDoc - template.csv)
VERSION INFO:
    Created by R. Reyna
    Date: 2024-07-22
    Version: 1.0
"""
import os
import shutil

filepath = "C:/Users/maiko/Desktop/The Vault/CodingPractice/Python/EditCSVForSera"
filepath_test = "C:/Users/maiko/Desktop/The Vault/CodingPractice/Python/EditCSVForSera/testFiles"
filename_orig = "testDoc.csv"
filename_edited = filename_orig[0:filename_orig.rfind(".")] + "_edited" + filename_orig[filename_orig.rfind("."):]
filename_log = filename_orig[0:filename_orig.rfind(".")] + "_log.txt"
filename_template = filename_orig[0:filename_orig.rfind(".")] + "_template" + filename_orig[filename_orig.rfind("."):]
absFilePath_orig = filepath + '/' + filename_orig
absFilePath_edited = filepath + '/' + filename_edited
absFilePath_log = filepath + '/' + filename_log
absFilePath_template = filepath_test + '/' + filename_template

# delete files
#filesToRemove = (filename_orig, filename_edited, filename_log)
filesToRemove = (absFilePath_orig, absFilePath_edited, absFilePath_log)
for file in filesToRemove:
    print(f"File {file}")
    if os.path.exists(file):
        os.remove(file)
        print("--cleaned up")
    else:
        print("--did not exist")

# create new test environment - copy/rename file
#shutil.copyfile(filename_template, filename_orig)
shutil.copyfile(absFilePath_template, absFilePath_orig)

