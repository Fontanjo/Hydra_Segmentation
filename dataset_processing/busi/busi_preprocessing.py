#########################################
#                                       #
#  Christophe Broillet                  #
#  University of Fribourg               #
#  2021                                 #
#  Bachelor's thesis                    #
#                                       #
#########################################

import numpy as np
import os
import glob
from PIL import Image
from pathlib import Path


arguments = {
    'dataset_folder': "/media/christophe/Extreme SSD/CancerDatasets/HealthyCopy/BUSI",
    'output_folder': "dataset_processing/busi/output",
    }

"""
Description: this script takes as input the BUSI dataset path,
and creates numpy arrays (images and segmentation masks)
in the given output folder
Params:
    dataset_folder   - Required  : folder containing the data set
    output_folder    - Required  : output folders
Returns:
    - No return value
"""
# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
output_folder = Path(arguments['output_folder'])

# Create directories in the output folder
os.makedirs(Path(f"{output_folder}/img"), exist_ok=True)
os.makedirs(Path(f"{output_folder}/masks"), exist_ok=True)

# List containing the 3 categories names
cat_names = os.listdir(dataset_folder)

# Number of total slices (images + masks)
ntotal = 0

# Number of images exported
nimgexported = 0

# Number of masks exported
nmasksexported = 0

# Iteration
for category in cat_names:
    # Construct the path
    category_path = Path(os.path.join(dataset_folder, category))

    # Increment ntotal
    ntotal = ntotal + len(os.listdir(category_path))

    # Create images path and masks path lists
    images_path_list = glob.glob(os.path.join(category_path, "*).png"))
    masks_path_list = glob.glob(os.path.join(category_path, "*mask*.png"))

    # Iteration over images
    for image_path in images_path_list:
        # Load file, using the path of the image, and the Image module
        image = Image.open(image_path)
        # Convert the image to 1 channel greyscale image (L for Luminance)
        image = image.convert('L')

        # Create destination file name
        fname = Path(image_path).stem
        # Create destination path
        dest = Path(os.path.join(output_folder, "img", f"{fname}.npy"))
        # Save the numpy array
        np.save(dest, image)

        # Print progress
        print('i', end='', flush=True)

        # Increment the number of exported files
        nimgexported += 1

    # Iteration over masks
    for mask_path in masks_path_list:
        # Load file, using the path of the mask, and the Image module
        image = Image.open(mask_path)
        # Convert the image to 1 channel greyscale image (L for Luminance)
        image = image.convert('L')

        # Create destination file name
        fname = Path(mask_path).stem
        # Create destination path
        dest = Path(os.path.join(output_folder, "masks", f"{fname}.npy"))
        # Save the numpy array
        np.save(dest, image)

        # Print progress
        print('m', end='', flush=True)

        # Increment the number of exported files
        nmasksexported += 1


# Sanity checks
print()
print(f"Total numbers of slices (ntotal): {ntotal}")
nimg = len(os.listdir(f"{output_folder}/img"))
nmasks = len(os.listdir(f"{output_folder}/masks"))
print(f"Expected: nimg + nmasks == ntotal")
print(f"{nimg} + {nmasks} = {nimg + nmasks} (expected {ntotal})")
if nimg + nmasks != ntotal:
    print('  ERROR! File numbers do not match!')
print()
