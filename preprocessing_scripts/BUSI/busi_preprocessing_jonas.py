import numpy as np
from PIL import Image
from pathlib import Path
import re


arguments = {
    # 'dataset_folder': "dataset_processing/busi/data",
    'dataset_folder': "/media/jonas/Seagate Expansion Drive/Memoria/master_thesis/Dataset_BUSI_with_GT",
    # 'output_folder': "dataset_processing/busi/output",
    'output_folder': "/media/jonas/Seagate Expansion Drive/Memoria/master_thesis/Dataset_BUSI_output",
    }


"""
Description: this script takes as input the BUSI dataset path,
and creates numpy arrays (images and segmentation masks)
in the given output folder
Params:
    dataset_folder   - Required  : folder containing the BUSI dataset
    output_folder    - Required  : output folder
Returns:
    - No return value
"""

"""
Modification Jonas:

Instead of discarding the images from the category 'normal', this are kept (and an empty mask is given)

Benignant and malignant tumor are created in different folders, and 'normal' images are splitted
 randomly in both

Images and masks are saved in the save folder
"""
# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
output_folder = Path(arguments['output_folder'])

# The slash operator '/' in the pathlib module is similar to os.path.join()
# images_output_path = output_folder / "img"
# masks_output_path = output_folder / "masks"
# Path.mkdir(images_output_path, exist_ok=True)
# Path.mkdir(masks_output_path, exist_ok=True)
Path.mkdir(output_folder, exist_ok=True)
Path.mkdir(output_folder / 'normal', exist_ok=True)
Path.mkdir(output_folder / 'malignant', exist_ok=True)
Path.mkdir(output_folder / 'benign', exist_ok=True)


# Define elementwise 'or' to merge masks, as vfunc
def elwise_or(a, b):
    return a or b

vfunc_or = np.vectorize(elwise_or)


# benign, malignant and normal
categories_names = Path.iterdir(dataset_folder)

ntotal = 0

for category_path in categories_names:
    # name returns a string representing the final path component
    # normal category have no tumors
    if category_path.name == 'normal':
        # TODO: Save randomly (or alternately) in begnignant/malignant folder
         # -> Better to do it with train/test/val preprocessing script
        images_output_path = output_folder / "normal"
    elif category_path.name == 'malignant':
        images_output_path = output_folder / "malignant"
    elif category_path.name == 'benign':
        images_output_path = output_folder / "benign"

    # Save masks with images
    masks_output_path = images_output_path

    # glob() matches files with the given pattern
    # It returns a generator containing the matched paths
    image_paths_list = category_path.glob("*(*).png")

    # Need to cast to list because generators do not have len()
    ntotal = ntotal + len(list(Path.iterdir(category_path)))

    for image_path in image_paths_list:
        image_name = image_path.name
        match = re.search(r"^([a-z]+) \(([0-9]+)\).png$", image_name)
        if match:
            # group(1,2) returns a tuple containing both groups submatches for the regex
            category, number = match.group(1,2)

            # Open, convert and save the image
            file_name = f"{category}{number}"
            destination_path = images_output_path / Path(file_name).with_suffix('.npy')
            image = Image.open(image_path)
            # L for Luminance, 8-bits pixels, 1-channel
            image = image.convert('L')
            np.save(destination_path, image)

            # Merge masks (elementwise or)
            mask_paths = category_path.glob(f"{category} ({number})_mask*.png")
            masks = []
            for index, mask_path in enumerate(mask_paths):
                # Open, convert and save the mask
                mask_name = file_name + f"_mask{index}"
                # mask_destination_path = masks_output_path / Path(mask_name).with_suffix('.npy')
                mask = Image.open(mask_path)
                # L for Luminance, 8-bits pixels, 1-channel
                mask = mask.convert('L')
                masks.append([mask_name, mask])

            if len(masks) == 1:
                np.save(masks_output_path / masks[0][0], masks[0][1])
            elif len(masks) > 1:
                mask_name = masks[0][0]
                mask = np.asarray(masks[0][1])
                for i in range(1, len(masks)):
                    mask = vfunc_or(mask, np.asarray(masks[i][1]))
                np.save(masks_output_path / mask_name, mask)
            else:
                print(f'No mask found for file {file_name}!!')

            print('.', end='', flush=True)


# Sanity checks
# print(f"\nTotal numbers of slices (ntotal): {ntotal}")
# nimg = len(list(Path.iterdir(images_output_path)))
# nmasks = len(list(Path.iterdir(masks_output_path)))
# print(f"Expected: nimg + nmasks == ntotal")
# print(f"{nimg} + {nmasks} = {nimg + nmasks} (expected {ntotal})")
# assert (nimg + nmasks) == ntotal, "File numbers do not match!"
