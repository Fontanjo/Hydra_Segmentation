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
from pathlib import Path

arguments = {
    'dataset_folder': "dataset_processing/headneck/test",
    'roinames_excel': "dataset_processing/headneck/INFO_GTVcontours_HN.xlsx",
    'output_folder': "dataset_processing/headneck/output",
    }

"""
Description: this script takes as input the Head-Neck-PET-CT dataset path,
the roi names excel file, and creates numpy arrays (images and segmentation masks)
in the given output folder
Params:
    dataset_folder   - Required  : folder containing the data set
    roinames_excel   - Required  : excel file containing the roi names information (given with the dataset)
    output_folder    - Required  : output folders
Returns:
    - No return value
"""
# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
roinames_excel = Path(arguments['roinames_excel'])
output_folder = Path(arguments['output_folder'])

# The slash operator '/' in the pathlib module is similar to os.path.join()
img_output_path = output_folder / 'img'
mask_output_path = output_folder / 'masks'
Path.mkdir(img_output_path, exist_ok=True)
Path.mkdir(mask_output_path, exist_ok=True)

print("\nGetting series UID and paths...\n", flush=True)

# Initialization
metadata_df = pd.DataFrame(columns=['Patient ID', 'Series UID', 'Modality', 'Associated series UID', 'Path', 'Roi name'])

# Import and combine the four excel sheets into a DataFrame
# Source : https://www.statology.org/combine-multiple-excel-sheets-pandas/
roi_excel_df = pd.concat(pd.read_excel(roinames_excel, sheet_name=None), ignore_index=True)

errors = []

# iterdir() is similar to os.listdir()
# Returns a generator object (function that behaves like an iterator)
for patient_path in Path.iterdir(dataset_folder):

    for patient_study_path in Path.iterdir(patient_path):

        for patient_study_serie_path in Path.iterdir(patient_study_path):
            # name returns a string representing the final path component
            patient_ID = patient_path.name

            # Open the first DICOM, and get the modality and the series UID
            dicom_path = next(Path.iterdir(patient_study_serie_path))
            dicom = pydicom.dcmread(dicom_path)
            # Dicom tags
            MODALITY = (0x8,0x60)
            SERIES_INSTANCE_UID = (0x20,0xe)
            modality = dicom[MODALITY].value
            serie_UID = dicom[SERIES_INSTANCE_UID].value

            # Get the roi name for this patient
            roi_name = roi_excel_df.loc[roi_excel_df['Patient'] == patient_ID, 'Name GTV Primary'].item()

            # Check the modality
            if modality in ['CT', 'PT']:
                # Add the row to the dataframe with informations
                metadata_df = metadata_df.append({
                    'Patient ID': patient_ID,
                    'Series UID': serie_UID,
                    'Modality': modality,
                    'Associated series UID': '',
                    'Path': patient_study_serie_path,
                    'Roi name': roi_name,
                }, ignore_index=True)

                print('.', end='', flush=True)
                continue

            elif modality == 'RTSTRUCT':
                # Get the image referenced UID
                REF_FRAME = (0x3006,0x10)
                REF_STUDY = (0x3006,0x12)
                REF_SERIES = (0x3006,0x14)
                # Use index 0, because dicom[] returns a list
                referenced_series = dicom[REF_FRAME][0][REF_STUDY][0][REF_SERIES][0]
                images_ref_UID = referenced_series[SERIES_INSTANCE_UID].value

                # Add the row to the dataframe with informations
                metadata_df = metadata_df.append({
                    'Patient ID': patient_ID,
                    'Series UID': serie_UID,
                    'Modality': modality,
                    'Associated series UID': images_ref_UID,
                    'Path': dicom_path,
                    'Roi name': roi_name,
                }, ignore_index=True)

                print('.', end='', flush=True)
                continue

            elif modality in ['RTPLAN', 'RTDOSE', 'REG']:
                print('.', end='', flush=True)
                continue

            else:
                errors.append(f"{patient_study_serie_path} is of modality {modality}")
                print('x', end='', flush=True)
                continue


print("\nCreating images and masks...\n", flush=True)


# RTStruct, images (CT + PET) separated in two dataframes
RT_df = metadata_df[metadata_df['Modality'] == 'RTSTRUCT']
images_df = metadata_df[(metadata_df['Modality'] == 'CT') |
                          (metadata_df['Modality'] == 'PT')]

# iterrows() iterates over DataFrame rows as (index, Series) pairs
for nrow, row_data in RT_df.iterrows():
    # Gather data
    patient_id, RT_series_UID, _modality, associated_series_UID, RT_path, ROI_name = row_data

    # Dicom tags for further use
    STRUCTURE_SET_ROI = (0x3006,0x20)
    ROI_NUMBER = (0x3006,0x22)
    ROI_NAME = (0x3006,0x26)
    ROI_CONTOUR_SEQUENCE = (0x3006,0x39)
    CONTOUR_SEQUENCE = (0x3006,0x40)
    CONTOUR_DATA = (0x3006,0x50)
    REF_ROI_NUMBER = (0x3006,0x84)
    CONTOUR_IMAGE = (0x3006,0x16)
    REF_SERIES_UID = (0x8,0x1155)
    SOP_INSTANCE_UID = (0x8,0x18)

    # Open the RTStruct file and get the structure set ROI
    dicom_RT = pydicom.dcmread(RT_path)
    struct_set_ROI = dicom_RT[STRUCTURE_SET_ROI]

    # Initialization
    ROI_number = ''

    for roi in struct_set_ROI:
        # Check if the ROI name correspond
        if roi[ROI_NAME].value == ROI_name:
            ROI_number = roi[ROI_NUMBER].value
            break

    for ROI_contour in dicom_RT[ROI_CONTOUR_SEQUENCE]:
        # Check if it is the ROI contour we want
        if ROI_contour[REF_ROI_NUMBER].value == ROI_number:

            for contour_sequence in ROI_contour[CONTOUR_SEQUENCE]:
                # Get the contour data, reshape and delete z coordinate
                contour_data = contour_sequence[CONTOUR_DATA].value
                contour_data = np.array(contour_data).reshape(-1,3)
                contour_data = np.delete(contour_data, -1, 1)
                contour_data = contour_data.astype('float')

                # Get the referenced image UID and the corresponding path
                ref_image_UID = contour_sequence[CONTOUR_IMAGE][0][REF_SERIES_UID].value
                series_images_path = Path(images_df.loc[images_df['Series UID'] == associated_series_UID, 'Path'].item())

                for image_path in Path.iterdir(series_images_path):
                    # Open the image DICOM and get its UID
                    dicom_image = pydicom.dcmread(image_path)
                    instance_UID = dicom_image[SOP_INSTANCE_UID].value

                    # Check if it is the image that we want
                    if instance_UID == ref_image_UID:
                        # Convert and save the image
                        slice_array = normalize_dicom.get_normalized_array(dicom_image)
                        modality = images_df.loc[images_df['Series UID'] == associated_series_UID, 'Modality'].item()
                        dest_fname_img = f"{patient_id}_modality-{modality}_UID-{instance_UID}_{nrow}"
                        dest_path_img = img_output_path / (dest_fname_img + '.npy')
                        np.save(dest_path_img, slice_array)

                        # Create segmentation mask and save it
                        dest_fname_mask = dest_fname_img + '_mask'
                        dest_path_mask = mask_output_path / (dest_fname_mask + '.npy')
                        mask_array = segmentation_mask.create_segmentation_mask(dicom_image, contour_data, output_folder, conversion=True)
                        np.save(dest_path_mask, mask_array)

                        print('v', end='', flush=True)
                        break
                    else:
                        print('.', end='', flush=True)
                        continue


# Sanity checks
print("\nList of errors :")
print(errors)

nimg = len(list(Path.iterdir(img_output_path)))
nmask = len(list(Path.iterdir(mask_output_path)))
print(f"\nExpected: nimg = nmask")
print(f"{nimg} = {nmask}")
assert nimg == nmask, "File numbers do not match!"
