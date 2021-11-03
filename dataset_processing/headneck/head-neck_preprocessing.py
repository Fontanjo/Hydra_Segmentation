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
import segmentationMask
import pandas as pd
import argparse


def main(dataset_folder, roinames_excel, output_folder):
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
    print("\nGetting series UID and paths...\n", flush=True)

    # Initialization
    metadata_df = pd.DataFrame(columns=['Patient ID', 'Series UID', 'Modality', 'Associated series UID', 'Path', 'Roi name'])

    # Import and combine the four excel sheets into one pandas DataFrame
    # Source : https://www.statology.org/combine-multiple-excel-sheets-pandas/
    roi_excel_df = pd.concat(pd.read_excel(roinames_excel, sheet_name=None), ignore_index=True)

    # Iterate over all patients
    for patient in os.listdir(dataset_folder):
        # Create the patient path
        patient_path = os.path.join(dataset_folder, patient)

        # Iterate over all studies
        for study in os.listdir(patient_path):
            # Create the study path
            patient_study_path = os.path.join(patient_path, study)

            # Iterate over all series
            for serie in os.listdir(patient_study_path):
                # Create the serie path
                patient_study_serie_path = os.path.join(patient_study_path, serie)

                # Name of the first DICOM of this serie
                dicom_name = os.listdir(patient_study_serie_path)[0]

                # Create the path to this DICOM
                dicom_path = os.path.join(patient_study_serie_path, dicom_name)

                # Open the DICOM
                dicom = pydicom.dcmread(dicom_path)

                # TODO: rename number with letter (dict or "global" variables (in upper case))
                # Example : MODALITY = (0x8, 0x60)

                # Get the modality of the DICOM
                modality = dicom[0x8,0x60].value

                # Get the series UID of the DICOM
                serie_UID = dicom[0x20,0xe].value

                # Get the roi name for this patient
                roi_name = roi_excel_df.loc[roi_excel_df['Patient'] == patient, 'Name GTV Primary'].item()

                # Check if the DICOM is a CT or a PET
                if modality in ['CT', 'PT']:
                    # Add the row to the dataframe with informations
                    metadata_df = metadata_df.append({
                        'Patient ID': patient,
                        'Series UID': serie_UID,
                        'Modality': modality,
                        'Associated series UID': '',
                        'Path': patient_study_serie_path,
                        'Roi name': roi_name,
                    }, ignore_index=True)

                    print('i', end='', flush=True)
                    continue

                if modality == 'RTSTRUCT':
                    # Get the UID of the referenced images of this RT Struct
                    # TODO : split and rename this line
                    images_ref_UID = dicom[0x3006,0x10][0][0x3006,0x12][0][0x3006,0x14][0][0x20,0xe].value

                    # Add the row to the dataframe with informations
                    # TODO : modify layout as above
                    metadata_df = metadata_df.append({
                        'Patient ID': patient,
                        'Series UID': serie_UID,
                        'Modality': modality,
                        'Associated series UID': images_ref_UID,
                        'Path': dicom_path,
                        'Roi name': roi_name
                    }, ignore_index=True)

                    print('r', end='', flush=True)
                    continue

                else:
                    # TODO : create a dictionnnary (?) erros, and append them (there can be a typo for example RTSRTUCT instead RTSTRUCT)
                    # Show the dictionnary errors at the end
                    print('.', end='', flush=True)
                    continue


    print("\nCreating images and masks...\n", flush=True)

    # Create a CT/PET directory (img) and a masks directory in the output folder
    os.makedirs(f"{output_folder}/img", exist_ok=True)
    os.makedirs(f"{output_folder}/masks", exist_ok=True)

    # Create a dataframe containing the RT Struct
    csv_RT = metadata_df[metadata_df['Modality'] == 'RTSTRUCT']

    # Create a dataframe containing the images (CT and PET)
    csv_images = metadata_df[(metadata_df['Modality'] == 'CT') |
                              (metadata_df['Modality'] == 'PT')]

    # Iterate over the rows of the RTStruct dataframe
    # iterrows() iterates over DataFrame rows as (index, Series) pairs
    for nrow, row_data in csv_RT.iterrows():
        # Gather data
        # strip() removes the spaces at the beginning and the end of the string
        patient_id = row_data['Patient ID'].strip()
        RT_series_UID = row_data['Series UID'].strip()
        associated_series_UID = row_data['Associated series UID'].strip()
        RT_path = row_data['Path'].strip()
        ROI_name = row_data['Roi name'].strip()

        # Open the RTStruct file
        dicom_RT = pydicom.dcmread(RT_path)

        # Get the Structure set ROI
        struct_set_ROI = dicom_RT[0x3006,0x20]

        # Will contain the ROI number
        ROI_number = ''

        # Iterate over the list of ROIs
        for roi in struct_set_ROI:
            # Check if the ROI name correspond
            if roi[0x3006,0x26].value == ROI_name:
                ROI_number = roi[0x3006,0x22].value
                break

        # Get the ROI contour sequence
        ROI_contour_sequence = dicom_RT[0x3006,0x39]

        # Iterate over the ROI_contour_sequence
        for ROI_contour in ROI_contour_sequence:
            # Check if it is the ROI contour we want
            if ROI_contour[0x3006,0x84].value == ROI_number:
                # Get the list of all referenced slices UID for this roi contour
                # slices_UID = [ROI_contour[0x3006,0x40][i][0x3006,0x16][0][0x8,0x1155].value for i in range(ROI_contour[0x3006,0x40].VM)]
                # print(slices_UID)

                # Iterate over all contour sequences
                for contour_sequence in ROI_contour[0x3006,0x40]:
                    # Get the contour data
                    contour_data = contour_sequence[0x3006,0x50].value

                    # Put it in an array and reshape it to 3D points
                    contour_data = np.array(contour_data).reshape(-1,3)

                    # Delete the z coordinate
                    contour_data = np.delete(contour_data, -1, 1)

                    # Cast the array to float
                    contour_data = contour_data.astype('float')

                    # Get the referenced image UID
                    ref_image_UID = contour_sequence[0x3006,0x16][0][0x8,0x1155].value

                    # Get the path of the associated images series (cast to string)
                    series_images_path = str(csv_images.loc[csv_images['Series UID'] == associated_series_UID, 'Path'].item())

                    # Iterate over all the images of the corresponding series
                    # TODO : if this is long: load all images at the same time ?
                    for image in os.listdir(series_images_path):
                        # Create the image path
                        image_path = os.path.join(series_images_path, image)

                        # Open the image DICOM
                        dicom_image = pydicom.dcmread(image_path)

                        # Get the instance UID of this image
                        instance_UID = dicom_image[0x8,0x18].value

                        # Check if it is the image that we want
                        if instance_UID == ref_image_UID:
                            # Get the normalized numpy array using own method
                            slice_ary = normalizeDicom.get_normalized_array(dicom_image)

                            # Get the modality
                            modality = csv_images.loc[csv_images['Series UID'] == associated_series_UID, 'Modality'].item()

                            # Create output name of the image, add nrow at the end to avoid duplication
                            dest_fname_img = f"{patient_id}_modality-{modality}_UID-{instance_UID}_{nrow}"

                            # Create path for the destination of the file
                            dest_img = os.path.join(output_folder, 'img', dest_fname_img)

                            # Save the numpy array slice with the dest_fname_img
                            np.save(dest_img, slice_ary)

                            # Create output name of the mask
                            dest_fname_mask = dest_fname_img + '_mask'

                            # Create path for the destination of the file
                            dest_mask = os.path.join(output_folder, 'masks', dest_fname_mask)

                            # Get the segmentation mask
                            mask_ary = segmentationMask.create_segmentation_mask(dicom_image, contour_data)

                            # Save the numpy array segmentation mask with the dest_fname_mask
                            np.save(dest_mask, mask_ary)

                            # Print progress
                            print('v', end='', flush=True)

                            break
                        else:
                            print('.', end='', flush=True)
                            continue


    # Sanity checks
    print()
    nimg = len(os.listdir(f"{output_folder}/img"))
    nmask = len(os.listdir(f"{output_folder}/masks"))
    print(f"Expected: nimg = nmask")
    print(f"{nimg} = {nmask}")
    if nimg != nmask:
        print('  ERROR! File numbers do not match!')
    print()


# TODO : put arguments as a dictionnary in top of the script, and remove all this stuff
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='')


    parser.add_argument('--datasetfolder',
                        help='Path to root of the dataset folder.',
                        required=True,
                        type=str
                        )

    parser.add_argument('--roinamesxlsx',
                        help='Path to the .xlsx file containing the ROI names, given with the dataset',
                        required=True,
                        type=str
                        )

    parser.add_argument('--outputfolder',
                        help='Path to output folder.',
                        required=True,
                        type=str
                        )

    args = parser.parse_args()

    main(args.datasetfolder, args.roinamesxlsx, args.outputfolder)
