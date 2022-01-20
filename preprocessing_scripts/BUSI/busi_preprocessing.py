import numpy as np
from PIL import Image
from pathlib import Path
import re


arguments = {
    'dataset_folder': "dataset_processing/busi/data",
    'output_folder': "dataset_processing/busi/output",
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
# Get the arguments
dataset_folder = Path(arguments['dataset_folder'])
output_folder = Path(arguments['output_folder'])

# The slash operator '/' in the pathlib module is similar to os.path.join()
images_output_path = output_folder / "img"
masks_output_path = output_folder / "masks"
Path.mkdir(images_output_path, exist_ok=True)
Path.mkdir(masks_output_path, exist_ok=True)

# benign, malignant and normal
categories_names = Path.iterdir(dataset_folder)

ntotal = 0

for category_path in categories_names:
    # name returns a string representing the final path component
    # normal category have no tumors
    if category_path.name == 'normal':
        continue

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

            # Can have more then 1 mask per image
            mask_paths = category_path.glob(f"{category} ({number})_mask*.png")
            for index, mask_path in enumerate(mask_paths):
                # Open, convert and save the mask
                mask_name = file_name + f"_mask{index}"
                mask_destination_path = masks_output_path / Path(mask_name).with_suffix('.npy')
                mask = Image.open(mask_path)
                # L for Luminance, 8-bits pixels, 1-channel
                mask = mask.convert('L')
                np.save(mask_destination_path, mask)

            print('.', end='', flush=True)


# Sanity checks
print(f"\nTotal numbers of slices (ntotal): {ntotal}")
nimg = len(list(Path.iterdir(images_output_path)))
nmasks = len(list(Path.iterdir(masks_output_path)))
print(f"Expected: nimg + nmasks == ntotal")
print(f"{nimg} + {nmasks} = {nimg + nmasks} (expected {ntotal})")
assert (nimg + nmasks) == ntotal, "File numbers do not match!"
