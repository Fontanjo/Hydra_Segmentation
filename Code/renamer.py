import pydicom
from pydicom.data import get_testdata_file
import os


path_to_dataset = "/home/christophe/Bureau/DataSet" # absolute path

for patient in os.listdir(path_to_dataset): # iterate over all patients
    for data in os.listdir(path_to_dataset + '/' + patient): # iterate over all dates
        for serie in os.listdir(path_to_dataset + '/' + patient + '/' + data): # iterate over all series
            dicom_names_list = os.listdir(path_to_dataset + '/' + patient + '/' + data + '/' + serie) # list all dicom files in the current serie
            ds = pydicom.dcmread(path_to_dataset + '/' + patient + '/' + data + '/' + serie + '/' + dicom_names_list[0]) # open a dicom file in the current serie
            new_name = ds.SeriesDescription.replace('/', '_') # replace '/' by '_' to avoid conflict
            os.rename(path_to_dataset + '/' + patient + '/' + data + '/' + serie, path_to_dataset + '/' + patient + '/' + data + '/' + new_name) # renaming the folder serie
