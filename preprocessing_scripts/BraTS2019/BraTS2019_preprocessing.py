import numpy as np
import pandas as pd
from xml.dom import minidom
from pathlib import Path
import nibabel as nib
import os
from tqdm import tqdm



arguments = {
    'dataset_folder': "/media/jonas/Seagate Expansion Drive/Memoria/master_thesis/DSetsCristophe/HealthyCopy/BraTS2019",
    'output_folder': "/media/jonas/Seagate Expansion Drive/Memoria/master_thesis/Dataset_BraTS2019_output",
    'min_mask_pixels': 20, # Minimum number of 'active' pixels in a mask to be kept
    }


"""
Description: this script takes as input the BraTS2019 dataset path,
and creates numpy arrays in the given output folder
Params:
    dataset_folder   - Required  : folder containing the data set
    output_folder    - Required  : output folders
Returns:
    - No return value


In the output folder, the results are separated as follows:

- Output_folder
    - HGG
        - flair
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
                - filename_slice_X_flair.npy
                - filename_slice_Y_flair.npy
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
                - filename_slice_W_flair.npy
                - filename_slice_Z_flair.npy
        - t1
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
                - filename_slice_X_t1.npy
                - filename_slice_Y_t1.npy
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
                - filename_slice_W_t1.npy
                - filename_slice_Z_t1.npy
        - t1ce
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
        - t2
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
        - mask
    - LGG
        - flair
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
        - t1
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
        - t1ce
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
        - t2
            - empty_mask    -> Images for which the mask is empty. This masks are NOT generated (# TODO script to generate them)
            - with_mask     -> Images for which the mask is not empty. This masks are in folder 'mask' with the same name (and '_mask' appended at the end)
        - mask
            - filename_slice_W.npy
            - filename_slice_Z.npy

"""



# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
output_folder = Path(arguments['output_folder'])


# Create folders
for grade in ['HGG', 'LGG']:
    # Images folder
    for type in ['t1', 't1ce', 't2', 'flair']:
        for mask_type in ['empty_mask', 'with_mask']:
            os.makedirs(f'{output_folder}/{grade}/{type}/{mask_type}', exist_ok=True)
    # Mask folder
    os.makedirs(f'{output_folder}/{grade}/mask', exist_ok=True)


# HGG / LGG
for grade_path in Path.iterdir(dataset_folder):
    # Count added
    nb_with_mask = 0
    nb_empty_mask = 0
    # Get grade name
    grade_name = str(grade_path).split('/')[-1]
    # Patient
    if not os.path.isdir(grade_path): continue
    for patient_path in Path.iterdir(grade_path):
        patient_name = str(patient_path).split('/')[-1]
        # Load data
        mask = nib.load(f'{patient_path}/{patient_name}_seg.nii').get_fdata()
        t1 = nib.load(f'{patient_path}/{patient_name}_t1.nii').get_fdata()
        t1ce = nib.load(f'{patient_path}/{patient_name}_t1ce.nii').get_fdata()
        t2 = nib.load(f'{patient_path}/{patient_name}_t2.nii').get_fdata()
        flair = nib.load(f'{patient_path}/{patient_name}_flair.nii').get_fdata()
        # Iterate over each slice
        for slice in tqdm(range(mask.shape[2])):
            # Check if the mask is empty or not
            is_mask = np.max(mask[:,:,slice]) > 0
            # mask_pixels = len(mask[:,:,slice][mask[:,:,slice] > 0])
            if is_mask: # and mask_pixels >= arguments['min_mask_pixels']:
                nb_with_mask += 1
                # Save slices
                np.save(f'{output_folder}/{grade_name}/t1/with_mask/{patient_name}_slice_{slice}_t1.npy', t1[:,:,slice])
                np.save(f'{output_folder}/{grade_name}/t1ce/with_mask/{patient_name}_slice_{slice}_t1ce.npy', t1ce[:,:,slice])
                np.save(f'{output_folder}/{grade_name}/t2/with_mask/{patient_name}_slice_{slice}_t2.npy', t2[:,:,slice])
                np.save(f'{output_folder}/{grade_name}/flair/with_mask/{patient_name}_slice_{slice}_flair.npy', flair[:,:,slice])
                # Save mask
                np.save(f'{output_folder}/{grade_name}/mask/{patient_name}_slice_{slice}_mask.npy', mask[:,:,slice]/4)
            else:
                nb_with_mask += 1
                # Save slices
                np.save(f'{output_folder}/{grade_name}/t1/empty_mask/{patient_name}_slice_{slice}_t1.npy', t1[:,:,slice])
                np.save(f'{output_folder}/{grade_name}/t1ce/empty_mask/{patient_name}_slice_{slice}_t1ce.npy', t1ce[:,:,slice])
                np.save(f'{output_folder}/{grade_name}/t2/empty_mask/{patient_name}_slice_{slice}_t2.npy', t2[:,:,slice])
                np.save(f'{output_folder}/{grade_name}/flair/empty_mask/{patient_name}_slice_{slice}_flair.npy', flair[:,:,slice])

    print(f'{nb_with_mask} images with masks added for {grade_name}')
    print(f'{nb_empty_mask} images without masks added for {grade_name}')

        # print(mask.shape)
