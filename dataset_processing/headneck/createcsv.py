#########################################
#                                       #
#  Christophe Broillet                  #
#  University of Fribourg               #
#  2021                                 #
#  Bachelor's thesis                    #
#                                       #
#########################################


import pydicom
import numpy as np
import os
from PIL import Image
# import normalizeDicom
import pandas as pd
import argparse
from tqdm import tqdm
import sys
import math
import glob
# cross-platform path
from pathlib import Path
from rt_utils import RTStructBuilder


def main(metadata_csv, roinames_csv, dataset_folder):
    """
    Description: this script takes as input the metadata csv file of the Head-Neck Pet/CT dataset and create
    a new csv file containing only the CT and his corresponding RTSTRUCT
    Params:
        metadata_csv     - Required  : csv file containing the metadata information
        dataset_folder   - Required  : folder containing the data set
    Returns:
        - No return value
    """
    # Read the metadata csv file and store it in a DataFrame
    csv_metadata = pd.read_csv(metadata_csv, sep=',', usecols=['Subject ID', 'Study UID', 'Series UID', 'Modality'])

    # Keep only the modality CT, PET and RTStruct in the DataFrame
    csv_metadata = csv_metadata[(csv_metadata['Modality'] == 'CT') | (csv_metadata['Modality'] == 'RTSTRUCT')]

    # Renaming column name Subject ID to Patient ID
    csv_metadata.rename(columns = {'Subject ID':'Patient ID'}, inplace = True)

    # Get the list of all patients
    patients_list = os.listdir(dataset_folder)

    # Iterate over all patients
    for patient in patients_list:
        # Create the patient path
        patient_path = os.path.join(dataset_folder, patient)

        # Get the list of all studies
        studies_list = os.listdir(patient_path)

        # Iterate over all studies
        for study in studies_list:
            # Create the study path
            patient_study_path = os.path.join(patient_path, study)

            # Get the list of all series
            series_list = os.listdir(patient_study_path)

            # List containing the UIDs of the CT of this study
            CT_UID_list = []

            # List containing lists of RT UID and their corresponding referenced CT series UID
            RT_CT_list = []

            # Iterate over all series
            for serie in series_list:
                # Create the serie path
                patient_study_serie_path = os.path.join(patient_study_path, serie)

                # Name of the first DICOM of this serie
                dicom_name = os.listdir(patient_study_serie_path)[0]

                # Create the path to this DICOM
                dicom_path = os.path.join(patient_study_serie_path, dicom_name)

                # Open the DICOM
                dicom = pydicom.dcmread(dicom_path)

                # Get the modality of the DICOM
                modality = dicom[0x8,0x60].value

                # Get the series UID
                serie_UID = dicom[0x20,0xe].value

                # Check if the DICOM is a CT
                if modality == 'CT':
                    # Add this CT UID to the list
                    CT_UID_list.append(serie_UID)
                    print('.', end='', flush=True)
                    continue
                elif modality == 'RTSTRUCT':
                    # Get the UID of the referenced images of this RT Struct
                    images_ref_UID = dicom[0x3006,0x10][0][0x3006,0x12][0][0x3006,0x14][0][0x20,0xe].value
                    # Add a doublet containing this RT UID and its corresponding images UID
                    RT_CT_list.append([serie_UID, images_ref_UID])
                    print('.', end='', flush=True)
                    continue
                else:
                    print('.', end='', flush=True)
                    continue

            # Iterate over the RT_CT_list
            for duplet in RT_CT_list:
                # Check if the image UID of the duplet is in the list
                if duplet[1] in CT_UID_list:
                    # Remove it from the list
                    CT_UID_list.remove(duplet[1])
                # Check if the image UID is not in the duplet
                elif duplet[1] not in CT_UID_list:
                    # Delete the corresponding row in the DataFrame
                    csv_metadata = csv_metadata[csv_metadata['Series UID'] != duplet[0]]
                    print('d', end='', flush=True)

            # Check if the image UID list is not empty
            if CT_UID_list != []:
                # Iterate over all elements left in the list
                for image_UID in CT_UID_list:
                    # Delete the corresponding row in the DataFrame
                    csv_metadata = csv_metadata[csv_metadata['Series UID'] != image_UID]
                    print('d', end='', flush=True)


    # Read the ROI names csv file
    csv_roinames = pd.read_csv(roinames_csv, sep=',', usecols=['Patient ID', 'Roi name primary', 'Roi name lymph node'])

    # Create a new roi name primary column
    csv_metadata['Roi name primary'] = csv_metadata['Modality']

    # Create a new roi name lymph node column
    csv_metadata['Roi name lymph node'] = csv_metadata['Modality']

    print('Saving csv file...')
    # Iterate over the rows of the metadata csv file
    for nrow, row in csv_metadata.iterrows():

        # Set the roi name primary
        csv_metadata.loc[nrow]['Roi name primary'] = csv_roinames[csv_roinames['Patient ID'] == row['Patient ID']].iloc[0]['Roi name primary']

        # Set the roi name lypmh node
        csv_metadata.loc[nrow]['Roi name lymph node'] = csv_roinames[csv_roinames['Patient ID'] == row['Patient ID']].iloc[0]['Roi name lymph node']

    # Save the dataframe in a new csv file
    csv_metadata.to_csv(r'CT_RT_infos.csv', index = False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='')


    parser.add_argument('--metadatacsv',
                        help='Path to the .csv file containing the metadata information',
                        required=True,
                        type=str
                        )

    parser.add_argument('--roinamescsv',
                        help='Path to the .csv file containing the ROI names',
                        required=True,
                        type=str
                        )

    parser.add_argument('--datasetfolder',
                        help='Path to root of the dataset folder.',
                        required=True,
                        type=str
                        )

    args = parser.parse_args()

    main(args.metadatacsv, args.roinamescsv, args.datasetfolder)
