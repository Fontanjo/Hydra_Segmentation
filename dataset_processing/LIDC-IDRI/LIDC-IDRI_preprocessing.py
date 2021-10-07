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
import normalizeDicom
import pandas as pd
import argparse
from tqdm import tqdm
import sys
import math
import glob
from xml.dom import minidom
# cross-platform path
from pathlib import Path


def main(dataset_folder, diagnosis_csv, output_folder):
    """
    Description: this script takes as input the LIDC-IDRI dataset path, the .csv containing the metadata information, and creates numpy arrays in the given output folder
    Params:
        dataset_folder   - Required  : folder containing the data set
        diagnosis_csv    - Required  : csv file containing the diagnosis information
        output_folder    - Required  : output folders
    Returns:
        - No return value
    """
    # Create a True/False directory in the output folder
    os.makedirs(f"{output_folder}/{True}", exist_ok=True)
    os.makedirs(f"{output_folder}/{False}", exist_ok=True)

    # Read the diagnosis csv file and store in a DataFrame
    csv_diagnosis = pd.read_csv(diagnosis_csv, sep=',', usecols=['Patient ID','Diagnosis'])

    # Number of nodules (will be incremented at runtime)
    nnodules = 0

    # Number of slices exported
    nexported = 0

    # Number of slices not found
    nnot_found_slices = 0

    # Iterate over the rows of the diagnosis csv file
    # iterrows() iterates over DataFrame rows as (index, Series) pairs
    for nrow, row_data in csv_diagnosis.iterrows():

        # Print progress
        if (nrow+1) % 10 == 0: print(f"\n  ROW {nrow+1}/{nnodules}")

        # Gather data
        # strip() removes the spaces at the beginning and the end of the string
        patient_id = row_data['Patient ID'].strip()
        diagnosis = int(row_data['Diagnosis'])

        # Convert labels into False/True labels for diagnosis
        if diagnosis == 1:
            diagnosis = False
        elif diagnosis in [2, 3]:
            diagnosis = True
        else:
            print('Unknown label, exiting...')
            exit(0)

        # Create the path for the corresponding patient_id
        patient_path = os.path.join(dataset_folder, patient_id)

        # For a patient ID, iterate over all visits
        for patient_visit in os.listdir(patient_path):
            if (patient_visit.startswith(".")):
                continue

            # Create the path for the patient visit
            patient_visit_path = os.path.join(patient_path, patient_visit)

            # Create the path for the unique serie of this visit
            patient_visit_serie_path = os.path.join(patient_visit_path, os.listdir(patient_visit_path)[0])

            # Check if this visit contains DX or CR scans
            if len(os.listdir(patient_visit_serie_path)) <= 10:
                print("\nDX or CR serie found, skip this visit")
                continue

            # Create the path of the xml file for this serie
            xml_path = glob.glob(os.path.join(patient_visit_serie_path, "*.xml"))[0]

            #Parse the xml file
            file = minidom.parse(xml_path)

            # Search for all 4 reading sessions
            reading_sessions = file.getElementsByTagName('readingSession')

            # Create a dataframe to store informations about all nodules for this serie
            nodules_df = pd.DataFrame(columns=['Nodule ID', 'x pos', 'y pos', 'z pos'])

            # Iterate over the 4 reading sessions
            for session in reading_sessions:
                # Search for all nodule ID
                nodules = session.getElementsByTagName('unblindedReadNodule')

                # Iterate over all nodules for this session
                for nodule in nodules:
                    # Get the nodule ID
                    nodule_id = nodule.getElementsByTagName('noduleID')[0].firstChild.data

                    # Search for all ROI's
                    slices = nodule.getElementsByTagName('roi')

                    # Iterate over all slices. Each slice will be one row in nodules_df
                    for slice in slices:
                        # Create an array to get all x and y coordinates of the edgeMaps
                        x_coords = np.array([])
                        y_coords = np.array([])
                        # Get all edgeMaps
                        edge_maps = slice.getElementsByTagName('edgeMap')

                        # Iterate over all edgeMaps
                        for edge_map in edge_maps:
                            # Get the xCoord value
                            x = int(edge_map.getElementsByTagName('xCoord')[0].firstChild.data)
                            # Get the yCoord value
                            y = int(edge_map.getElementsByTagName('yCoord')[0].firstChild.data)
                            # Add the values to the corresponding array
                            x_coords = np.append(x_coords, x)
                            y_coords = np.append(y_coords, y)

                        # Compute the center of the nodule in this slice
                        center_x = int(np.sum(x_coords) / len(x_coords))
                        center_y = int(np.sum(y_coords) / len(y_coords))

                        # Get the z coordinates of this slice
                        center_z = float(slice.getElementsByTagName('imageZposition')[0].firstChild.data)

                        # Add a new row in the nodules dataframe
                        nodules_df.loc[len(nodules_df.index)] = [nodule_id, center_x, center_y, center_z]


            nnodules = nnodules + len(nodules_df)

            # Iterate over the rows of the nodules dataframe
            for index, nodule_info in nodules_df.iterrows():
                # Extract the infos for this row
                nid = nodule_info[0]
                pos_x = nodule_info[1]
                pos_y = nodule_info[2]
                pos_z = nodule_info[3]

                # Boolean that indicates if the slice was found
                sliceFound = False

                # Iterate over all dicom files
                for dicom_path in glob.glob(os.path.join(patient_visit_serie_path, "*.dcm")):
                    # Load the file
                    dcm = pydicom.read_file(dicom_path)

                    # Get the z position of this dicom image
                    dcm_z_position = float(dcm[0x20, 0x32].value[2])

                    # Check if it is the right slide
                    if dcm_z_position == pos_z:
                        # Use for counting errors
                        sliceFound = True

                        # Get the normalized numpy array using own method
                        slice_ary = normalizeDicom.get_normalized_array(dcm)

                        # Create output name, add nrow at the end to avoid duplication
                        dest_fname = f"{patient_id}_nid-{nid}_pos-{pos_x}-{pos_y}_slice-{dcm_z_position}"
                        # Create path for the destination of the file
                        # dest = Path(f"{output_folder}/{diagnosis}/{dest_fname}")
                        dest = os.path.join(output_folder, str(diagnosis), dest_fname)

                        # Save the numpy array with the dest_fname
                        np.save(dest, slice_ary)

                        # Print progress
                        print('v', end='', flush=True)

                        # Increment the number of exported files
                        nexported += 1

                        break
                    else:
                        print('.', end='', flush=True)

                # if the slice was not found in the repository
                if not sliceFound:
                    nnot_found_slices += 1


    # Sanity checks
    print()
    print(f"Total numbers of nodules (nnodules): {nnodules}")
    print(f"Expected: nexported + nnot_found_slices == nnodules")
    print(f"{nexported} + {nnot_found_slices} = {nexported + nnot_found_slices} (expected {nnodules})")
    if nexported + nnot_found_slices != nnodules:
        print('  ERROR! Array sizes do not match!')
    print()

    ntrue = len(os.listdir(f"{output_folder}/{True}"))
    nfalse = len(os.listdir(f"{output_folder}/{False}"))
    print(f"Expected: ntrue + nfalse == nexported")
    print(f"{ntrue} + {nfalse} = {ntrue + nfalse} (expected {nexported})")
    if ntrue + nfalse != nexported:
        print('  ERROR! File numbers do not match!')
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='')

    parser.add_argument('--datasetfolder',
                        help='Path to root of the dataset folder.',
                        required=True,
                        type=str
                        )

    parser.add_argument('--diagnosiscsv',
                        help='Path to the .csv file containing the diagnosis labels',
                        required=True,
                        type=str
                        )

    parser.add_argument('--outputfolder',
                        help='Path to output folder.',
                        required=True,
                        type=str
                        )

    args = parser.parse_args()

    main(args.datasetfolder, args.diagnosiscsv, args.outputfolder)
