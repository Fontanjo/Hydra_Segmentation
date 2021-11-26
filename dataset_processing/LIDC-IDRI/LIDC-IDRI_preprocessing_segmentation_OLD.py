#########################################
#                                       #
#  Christophe Broillet                  #
#  University of Fribourg               #
#  2022                                 #
#  Bachelor's thesis                    #
#                                       #
#########################################


import pydicom
import numpy as np
import normalize_dicom
import segmentation_mask
import pandas as pd
from xml.dom import minidom
from pathlib import Path


arguments = {
    'dataset_folder': "dataset_processing/LIDC-IDRI/test",
    # 'dataset_folder': "/media/christophe/Extreme SSD/CancerDatasets/HealthyCopy/LIDC-IDRI/LIDC-IDRI",
    'output_folder': "dataset_processing/LIDC-IDRI/output_segmentation",
    }

"""
Description: this script takes as input the LIDC-IDRI dataset path,
and creates numpy arrays (images and segmentation masks) in the given output folder
Params:
    dataset_folder   - Required  : folder containing the data set
    output_folder    - Required  : output folders
Returns:
    - No return value
"""
# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
output_folder = Path(arguments['output_folder'])

# The slash operator '/' in the pathlib module is similar to os.path.join()
img_output_path = output_folder / 'img'
mask_output_path = output_folder / 'masks'
Path.mkdir(img_output_path, exist_ok=True)
Path.mkdir(mask_output_path, exist_ok=True)

# nnodules incremented at run time
nnodules = 0
nexported = 0
nnot_found_slices = 0
errors = []

# iterdir() is similar to os.listdir()
# Returns a generator object (function that behaves like an iterator)
for patient_path in Path.iterdir(dataset_folder):
    print("\nParsing XML file:\n", flush=True)

    for patient_study_path in Path.iterdir(patient_path):

        for patient_study_serie_path in Path.iterdir(patient_study_path):
            # Check if this visit contains DX or CR scans
            # Need to cast to list because generators do not have len()
            if len(list(Path.iterdir(patient_study_serie_path))) <= 10:
                print("\nDX or CR serie found, skip this visit")
                continue

            # glob() matches files with the given pattern
            # It returns a generator containing the matched paths
            # Cast to a list for the following use
            xml_list = list(patient_study_serie_path.glob("*.xml"))
            xml_len = len(xml_list)
            if xml_len != 1:
                errors.append(f"{patient_study_serie_path} has {xml_len} XML files")
                continue
            xml_path = xml_list[0]

            # parse() does not take Path() objects, so convert it to string
            file = minidom.parse(str(xml_path))

            # Create a dataframe to store informations about all nodules for this series
            nodules_df = pd.DataFrame(columns=['Nodule ID', 'contour data', 'z pos'])

            # Search for all 4 reading sessions
            reading_sessions = file.getElementsByTagName('readingSession')

            for session in reading_sessions:
                # Search for nodules
                nodules = session.getElementsByTagName('unblindedReadNodule')

                for nodule in nodules:
                    # Nodules >=3mm have characteristics. If it is empty, we skip it
                    if nodule.getElementsByTagName('characteristics') == []:
                        print('.', end='', flush=True)
                        continue
                    # Get the nodule ID and malignancy,
                    # then set the diagnosis depending on the malignancy
                    nodule_id = nodule.getElementsByTagName('noduleID')[0].firstChild.data
                    malignancy = nodule.getElementsByTagName('malignancy')[0].firstChild.data

                    if malignancy not in ['1', '2', '3', '4', '5']:
                        errors.append(f"{patient_study_serie_path} has nodule {nodule_id} with unknow malignancy")
                    # Not a tumor, skip it
                    if malignancy in ['1','2','3']:
                        continue

                    # Search for all slices (roi)
                    slices = nodule.getElementsByTagName('roi')
                    # Each slice will be one row in nodules_df
                    for slice in slices:
                        # Initialization
                        contour_points = []
                        # Get all edgeMaps
                        edge_maps = slice.getElementsByTagName('edgeMap')
                        for edge_map in edge_maps:
                            # Add the values to the corresponding array
                            x = int(edge_map.getElementsByTagName('xCoord')[0].firstChild.data)
                            y = int(edge_map.getElementsByTagName('yCoord')[0].firstChild.data)
                            contour_points.append([x, y])

                        center_z = float(slice.getElementsByTagName('imageZposition')[0].firstChild.data)

                        # Add a new row in the nodules dataframe
                        nodules_df = nodules_df.append({
                            'Nodule ID': nodule_id,
                            'contour data': contour_points,
                            'z pos': center_z,
                        }, ignore_index=True)

                        print('.', end='', flush=True)

            # To check errors at the end
            nnodules = nnodules + len(nodules_df)

            print("\nSearching slices:\n", flush=True)

            # Iteration over the nodules dataframe
            for index, nodule_info in nodules_df.iterrows():
                # Extract the infos for this row
                nid = nodule_info['Nodule ID']
                contour_data = nodule_info['contour data']
                pos_z = nodule_info['z pos']
                # To check errors
                sliceFound = False

                dicom_paths_list = patient_study_serie_path.glob("*.dcm")

                for dicom_path in dicom_paths_list:
                    # Load dicom and get the z position
                    dcm = pydicom.dcmread(dicom_path)
                    IMAGE_POSITION = (0x20,0x32)
                    # Image position tag returns (x,y,z), so take value[2]
                    dcm_z_position = dcm[IMAGE_POSITION].value[2]

                    # Check if it is the slice that we want
                    if dcm_z_position == pos_z:
                        # Convert and save the image
                        # name returns a string representing the final path component
                        # Add index at the end to avoid duplicates
                        dest_fname_img = f"{patient_path.name}_nid-{nid}_pos-{pos_z}_{index}"
                        # with_suffix() returns a new path with the suffix changed (or added)
                        slice_array = normalize_dicom.get_normalized_array(dcm)
                        dest_path_img = img_output_path / Path(dest_fname_img + '.npy')
                        np.save(dest_path_img, slice_array)

                        # Create segmentation mask and save it
                        dest_fname_mask = dest_fname_img + '_mask'
                        dest_path_mask = mask_output_path / Path(dest_fname_mask + '.npy')
                        # Contour points already converted, no conversion needed
                        mask_array = segmentation_mask.create_segmentation_mask(dcm, contour_data, output_folder, conversion=False)
                        np.save(dest_path_mask, mask_array)

                        # To count the errors
                        sliceFound = True
                        print('v', end='', flush=True)
                        nexported += 1
                        break
                    else:
                        print('.', end='', flush=True)

                # If the slice was not found in the repository
                if not sliceFound:
                    errors.append(f"{patient_study_serie_path} slice in position z {pos_z} not found")
                    nnot_found_slices += 1


# Sanity checks
print("\nList of errors :")
print(errors)
print(f"\nTotal numbers of nodules (nnodules): {nnodules}")
print(f"Expected: nexported + nnot_found_slices == nnodules")
print(f"{nexported} + {nnot_found_slices} = {nexported + nnot_found_slices} (expected {nnodules})")
assert nexported + nnot_found_slices == nnodules, "Slices number do not match!"

nimg = len(list(Path.iterdir(img_output_path)))
nmask = len(list(Path.iterdir(mask_output_path)))
print(f"\nExpected: nimg = nmask")
print(f"{nimg} = {nmask}")
assert nimg == nmask, "File numbers do not match!"
