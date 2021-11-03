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
import normalizeDicom
import pandas as pd
import argparse
import glob
from xml.dom import minidom
# cross-platform path
# from pathlib import Path


def main(dataset_folder, output_folder):
    """
    Description: this script takes as input the LIDC-IDRI dataset path,
    and creates numpy arrays in the given output folder
    Params:
        dataset_folder   - Required  : folder containing the data set
        output_folder    - Required  : output folders
    Returns:
        - No return value
    """
    # Create a True/False directory in the output folder
    os.makedirs(f"{output_folder}/{True}", exist_ok=True)
    os.makedirs(f"{output_folder}/{False}", exist_ok=True)

    # Number of nodules (will be incremented at runtime)
    nnodules = 0
    # Number of slices exported
    nexported = 0
    # Number of slices not found
    nnot_found_slices = 0

    # Iterate over all patients
    for patient in os.listdir(dataset_folder):
        # Create the path for the corresponding patient
        patient_path = os.path.join(dataset_folder, patient)

        print("\nParsing all XML files...\n", flush=True)

        # For a patient, iterate over all visits
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

            # Parse the xml file
            file = minidom.parse(xml_path)

            # Search for all 4 reading sessions
            reading_sessions = file.getElementsByTagName('readingSession')

            # Create a dataframe to store informations about all nodules for this serie
            nodules_df = pd.DataFrame(columns=['Nodule ID', 'x pos', 'y pos', 'z pos', 'Diagnosis'])

            # Iterate over the 4 reading sessions
            for session in reading_sessions:
                # Search for all nodules
                nodules = session.getElementsByTagName('unblindedReadNodule')

                # Iterate over all nodules for this session
                for nodule in nodules:
                    # Nodules >=3mm have characteristics. If it is empty, we skip it
                    if nodule.getElementsByTagName('characteristics') == []:
                        print('.', end='', flush=True)
                        continue
                    # Get the nodule ID
                    nodule_id = nodule.getElementsByTagName('noduleID')[0].firstChild.data
                    # Get the malignancy
                    malignancy = nodule.getElementsByTagName('malignancy')[0].firstChild.data
                    # Initialization
                    diagnosis = True
                    # Change the diagnosis depending on the malignancy
                    if malignancy in ['1','2']:
                        diagnosis = False
                    # Uncertain, do not take this nodule
                    elif malignancy == '3':
                        continue
                    elif malignancy in ['4','5']:
                        diagnosis = True
                    # Malignancy not recognized
                    else:
                        continue

                    # Search for all roi's/slices
                    slices = nodule.getElementsByTagName('roi')
                    # Iterate over all slices. Each slice will be one row in nodules_df
                    for slice in slices:
                        # Create arrays to get all coordinates of nodule
                        x_coords = np.array([])
                        y_coords = np.array([])
                        # Get all edgeMaps
                        edge_maps = slice.getElementsByTagName('edgeMap')
                        for edge_map in edge_maps:
                            # Add the values to the corresponding array
                            x = int(edge_map.getElementsByTagName('xCoord')[0].firstChild.data)
                            y = int(edge_map.getElementsByTagName('yCoord')[0].firstChild.data)
                            x_coords = np.append(x_coords, x)
                            y_coords = np.append(y_coords, y)

                        # Compute the center of the nodule in this slice
                        # TODO : mean method of numpy
                        center_x = int(np.sum(x_coords) / len(x_coords))
                        center_y = int(np.sum(y_coords) / len(y_coords))

                        # Get the z coordinate of this slice
                        center_z = float(slice.getElementsByTagName('imageZposition')[0].firstChild.data)

                        # Add a new row in the nodules dataframe
                        # nodules_df.loc[len(nodules_df.index)] = [nodule_id, center_x, center_y, center_z, diagnosis]
                        nodules_df = nodules_df.append({
                            'Nodule ID': nodule_id,
                            'x pos': center_x,
                            'y pos': center_y,
                            'z pos': center_z,
                            'Diagnosis': diagnosis,
                        }, ignore_index=True)

                        print('p', end='', flush=True)


            # Increment the number of nodules
            nnodules = nnodules + len(nodules_df)

            print("\nSearching slices...\n", flush=True)

            # Iterate over the rows of the nodules dataframe
            for index, nodule_info in nodules_df.iterrows():
                # Extract the infos for this row
                nid = nodule_info[0]
                pos_x = nodule_info[1]
                pos_y = nodule_info[2]
                pos_z = nodule_info[3]
                diag = nodule_info[4]

                # Boolean that indicates if the slice was found
                sliceFound = False

                # Iterate over all dicom files
                for dicom_path in glob.glob(os.path.join(patient_visit_serie_path, "*.dcm")):
                    # Load the file
                    dcm = pydicom.dcmread(dicom_path)

                    # Get the z position of this dicom image
                    dcm_z_position = float(dcm[0x20, 0x32].value[2])

                    # Check if it is the slide that we want
                    if dcm_z_position == pos_z:
                        # Used for counting errors
                        sliceFound = True

                        # Get the normalized numpy array using own method
                        slice_ary = normalizeDicom.get_normalized_array(dcm)

                        # Create output name
                        dest_fname = f"{patient}_nid-{nid}_pos-{pos_x}-{pos_y}_slice-{dcm_z_position}"

                        # Create path for the destination of the file
                        # dest = Path(f"{output_folder}/{diagnosis}/{dest_fname}")
                        dest = os.path.join(output_folder, str(diag), dest_fname)

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
        print('  ERROR! Slices number do not match!')
    print()

    ntrue = len(os.listdir(f"{output_folder}/{True}"))
    nfalse = len(os.listdir(f"{output_folder}/{False}"))
    print(f"Expected: ntrue + nfalse == nexported")
    print(f"{ntrue} + {nfalse} = {ntrue + nfalse} (expected {nexported})")
    if ntrue + nfalse != nexported:
        print('  ERROR! File numbers do not match!')
    print()

# TODO : remove all this stuff and dictionnary with arguments at the top
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='')

    parser.add_argument('--datasetfolder',
                        help='Path to root of the dataset folder.',
                        required=True,
                        type=str
                        )

    parser.add_argument('--outputfolder',
                        help='Path to output folder.',
                        required=True,
                        type=str
                        )

    args = parser.parse_args()

    main(args.datasetfolder, args.outputfolder)
