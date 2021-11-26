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
    'output_folder': "dataset_processing/LIDC-IDRI/output",
    }

"""
Description: this script takes as input the LIDC-IDRI dataset path,
and creates numpy arrays in the given output folder
Params:
    dataset_folder   - Required  : folder containing the data set
    output_folder    - Required  : output folders
Returns:
    - No return value
"""
# Ask the user which task he wants
task = input("\n Please enter task. Localization (l) or segmentation (s)?")
while task not in ['l', 's']:
    task = input("\n Please enter a valid task. Localization (l) or segmentation (s)?")
if task == 'l': task = 'localization'
elif task == 's': task = 'segmentation'
print(f"\n Starting {task} task:")


# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
output_folder = Path(arguments['output_folder'])

# The slash operator '/' in the pathlib module is similar to os.path.join()
if task == 'localization':
    localization_path = output_folder / 'localization'
    Path.mkdir(localization_path, exist_ok=True)
    true_output_path = localization_path / 'True'
    false_output_path = localization_path / 'False'
    Path.mkdir(true_output_path, exist_ok=True)
    Path.mkdir(false_output_path, exist_ok=True)
elif task == 'segmentation':
    segmentation_path = output_folder / 'segmentation'
    Path.mkdir(segmentation_path, exist_ok=True)
    img_output_path = segmentation_path / 'img'
    mask_output_path = segmentation_path / 'masks'
    Path.mkdir(img_output_path, exist_ok=True)
    Path.mkdir(mask_output_path, exist_ok=True)
else:
    assert False, "Task misspelled"

# nnodules incremented at run time
nnodules = 0
nexported = 0
nnot_found_slices = 0
errors = []

# iterdir() is similar to os.listdir()
# Returns a generator object (function that behaves like an iterator)
for patient_path in Path.iterdir(dataset_folder):

    for patient_visit_path in Path.iterdir(patient_path):

        for patient_visit_serie_path in Path.iterdir(patient_visit_path):
            # Check if this visit contains DX or CR scans
            # Need to cast to list because generators do not have len()
            if len(list(Path.iterdir(patient_visit_serie_path))) <= 10:
                print("\nDX or CR serie found, skip this visit")
                continue

            # glob() matches files with the given pattern
            # It returns a generator containing the matched paths
            # Cast to a list for the following use
            xml_list = list(patient_visit_serie_path.glob("*.xml"))
            xml_len = len(xml_list)
            if xml_len != 1:
                errors.append(f"{patient_visit_serie_path} has {xml_len} XML files")
                continue
            xml_path = xml_list[0]

            print("\nParsing XML file:\n", flush=True)

            # parse() does not take Path() objects, so convert it to string
            file = minidom.parse(str(xml_path))

            # Create a dataframe to store informations about all nodules for this series
            if task == 'localization':
                nodules_df = pd.DataFrame(columns=['Nodule ID', 'x pos', 'y pos', 'z pos', 'Diagnosis'])
            elif task == 'segmentation':
                nodules_df = pd.DataFrame(columns=['Nodule ID', 'contour data', 'z pos'])
            else:
                assert False, "Task misspelled"

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
                    nodule_id = nodule.getElementsByTagName('noduleID')[0].firstChild.data
                    malignancy = nodule.getElementsByTagName('malignancy')[0].firstChild.data

                    if task == 'localization':
                        # Initialization
                        # then set the diagnosis depending on the malignancy
                        diagnosis = ''
                        if malignancy in ['1','2']:
                            diagnosis = 'False'
                        # Uncertain diagnosis, skip this nodule
                        elif malignancy == '3':
                            continue
                        elif malignancy in ['4','5']:
                            diagnosis = 'True'
                        else:
                            errors.append(f"{patient_visit_serie_path} has nodule {nodule_id} with unknown malignancy")

                    elif task == 'segmentation':
                        if malignancy not in ['1', '2', '3', '4', '5']:
                            errors.append(f"{patient_study_serie_path} has nodule {nodule_id} with unknow malignancy")
                        # Not a tumor, skip it
                        if malignancy in ['1','2','3']:
                            continue
                    else:
                        assert False, "Task misspelled"

                    # Search for all slices (roi)
                    slices = nodule.getElementsByTagName('roi')
                    # Each slice will be one row in nodules_df
                    for slice in slices:
                        # Initialization
                        if task == 'localization':
                            x_coords = []
                            y_coords = []
                        elif task == 'segmentation':
                            contour_points = []
                        else:
                            assert False, "Task misspelled"

                        # Get all edgeMaps
                        edge_maps = slice.getElementsByTagName('edgeMap')
                        for edge_map in edge_maps:
                            # Add the values to the corresponding array
                            x = int(edge_map.getElementsByTagName('xCoord')[0].firstChild.data)
                            y = int(edge_map.getElementsByTagName('yCoord')[0].firstChild.data)
                            if task == 'localization':
                                x_coords = np.append(x_coords, x)
                                y_coords = np.append(y_coords, y)
                            elif task == 'segmentation':
                                contour_points.append([x, y])
                            else:
                                assert False, "Task misspelled"

                        if task == 'localization':
                            # Compute the center coordinates of the nodule in this slice
                            center_x = np.mean(x_coords, dtype=np.int32)
                            center_y = np.mean(y_coords, dtype=np.int32)

                        center_z = float(slice.getElementsByTagName('imageZposition')[0].firstChild.data)

                        # Add a new row in the nodules dataframe
                        if task == 'localization':
                            nodules_df = nodules_df.append({
                                'Nodule ID': nodule_id,
                                'x pos': center_x,
                                'y pos': center_y,
                                'z pos': center_z,
                                'Diagnosis': diagnosis,
                            }, ignore_index=True)
                        elif task == 'segmentation':
                            nodules_df = nodules_df.append({
                                'Nodule ID': nodule_id,
                                'contour data': contour_points,
                                'z pos': center_z,
                            }, ignore_index=True)
                        else:
                            assert False, "Task misspelled"

                        print('.', end='', flush=True)

            # To check errors at the end
            nnodules = nnodules + len(nodules_df)

            print("\nSearching slices:\n", flush=True)

            # Iteration over the nodules dataframe
            # TODO: check instead of iterrows that returns a dict
            # TODO: better way than the index?
            for row_number, nodule_info in nodules_df.iterrows():
                # Extract the infos for this row
                if task == 'localization':
                    nid, pos_x, pos_y, pos_z, diag = nodule_info
                elif task == 'segmentation':
                    nid, contour_data, pos_z = nodule_info
                else:
                    assert False, "Task misspelled"

                # To check errors
                sliceFound = False

                dicom_paths_list = patient_visit_serie_path.glob("*.dcm")

                for dicom_path in dicom_paths_list:
                    # Load dicom and get the z position
                    dcm = pydicom.dcmread(dicom_path)
                    IMAGE_POSITION = (0x20,0x32)
                    # Used for further comparison
                    _x, _y, dcm_z_position = dcm[IMAGE_POSITION].value

                    # Check if it is the slice that we want
                    if dcm_z_position == pos_z:
                        # Convert and save the image
                        slice_array = normalize_dicom.get_normalized_array(dcm)
                        if task == 'localization':
                            # name returns a string representing the final path component
                            # Add row_number at the end to avoid duplicates
                            dest_fname_img = f"{patient_path.name}_nid-{nid}_pos-{pos_x}-{pos_y}_{row_number}.npy"
                            dest_path_img = localization_path / diag / dest_fname_img
                        elif task == 'segmentation':
                            dest_fname_img = f"{patient_path.name}_nid-{nid}_pos-{pos_z}_{row_number}"
                            dest_path_img = img_output_path / (dest_fname_img + '.npy')
                            # Save also mask for segmentation
                            dest_fname_mask = dest_fname_img + '_mask.npy'
                            dest_path_mask = mask_output_path / dest_fname_mask
                            # Contour points already converted, no conversion needed
                            mask_array = segmentation_mask.create_segmentation_mask(dcm, contour_data, output_folder, conversion=False)
                            np.save(dest_path_mask, mask_array)
                        else:
                            assert False, "Task misspelled"
                        np.save(dest_path_img, slice_array)

                        # To count the errors
                        sliceFound = True
                        print('v', end='', flush=True)
                        nexported += 1
                        break
                    else:
                        print('.', end='', flush=True)

                # If the slice was not found in the repository
                if not sliceFound:
                    errors.append(f"{patient_visit_serie_path} slice in position z {pos_z} not found")
                    nnot_found_slices += 1


# Sanity checks
print("\nList of errors :")
print(errors)
print(f"\nTotal numbers of nodules (nnodules): {nnodules}")
print(f"Expected: nexported + nnot_found_slices == nnodules")
print(f"{nexported} + {nnot_found_slices} = {nexported + nnot_found_slices} (expected {nnodules})")
assert nexported + nnot_found_slices == nnodules, "Slices number do not match!"

if task == 'localization':
    ntrue = len(list(Path.iterdir(true_output_path)))
    nfalse = len(list(Path.iterdir(false_output_path)))
    print(f"\nExpected: ntrue + nfalse == nexported")
    print(f"{ntrue} + {nfalse} = {ntrue + nfalse} (expected {nexported})")
    assert ntrue + nfalse == nexported, "File numbers do not match!"
elif task == 'segmentation':
    nimg = len(list(Path.iterdir(img_output_path)))
    nmask = len(list(Path.iterdir(mask_output_path)))
    print(f"\nExpected: nimg = nmask")
    print(f"{nimg} = {nmask}")
    assert nimg == nmask, "File numbers do not match!"
else:
    assert False, "Task misspelled"
