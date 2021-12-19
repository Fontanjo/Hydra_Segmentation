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
import pandas as pd
from pathlib import Path


def create_segmentation_mask(image, contour_data, output_folder, conversion):
    """Get normalized NumPy array segmentation mask from DICOM file and contour data
    @params:
        image          - Required : image (Pydicom) corresponding to one specific slice
        contour_data   - Required : 2D array containing contours points of the segmentation
        output_folder  - Required : Path to the output folder that will contain the log files
        conversion     - Required : Boolean that indicates if we want conversion or not
    """
    # Create and open a log text file
    # The slash operator '/' in the pathlib module is similar to os.path.join()
    logs_folder_path = Path(output_folder) / "segmentationMasksLogs"
    Path.mkdir(logs_folder_path, exist_ok=True)
    # Unique file name
    UID = (0x8, 0x18)
    file_name = Path(f"{image[UID].value}_logs.txt")
    file_path = logs_folder_path / file_name
    file = open(file_path, mode='w')

    # Initialization
    nrow = image.Rows
    ncol = image.Columns
    # Black pixel is of value 0
    seg_mask = np.zeros((nrow, ncol))

    # Draw contour
    for point in contour_data:
        # BEWARE : The x-coordinate corresponds to the COLUMN index,
        # and the y-coordinate corresponds to the ROW index
        if conversion:
            x, y = mm_to_imagecoordinates(image, point)
        else:
            x, y = point
        # White pixel is of value 255
        seg_mask[y][x] = 255


    # -- DATA MITIGATION AND IMPUTATION in two parts --
    # 1) Check and add if empty lines

    # White boundaries for each row of the image
    # Will contain lists [row mask index, min white column index, max white column index]
    white_boundaries = []
    # Source : https://stackoverflow.com/questions/34126230/getting-indices-of-a-specific-value-in-numpy-array
    white_indices = lambda row : np.argwhere(row == 255).flatten()
    min_mask = lambda row : np.min(white_indices(row))
    max_mask = lambda row : np.max(white_indices(row))

    for index, row in enumerate(seg_mask):
        # Row is full black
        if white_indices(row).size == 0:
            continue
        else:
            white_boundaries.append([index, min_mask(row), max_mask(row)])

    # To ensure the right order
    white_boundaries.sort(key=lambda x : x[0])

    # Iteration taking 2 tuples at a time
    for first, second in zip(white_boundaries, white_boundaries[1:]):
        first_index, first_min, first_max = first
        second_index, second_min, second_max = second

        # Check if rows are missing
        if abs(first_index - second_index) != 1:
            # Compute min and max means of the neighbours boundaries
            average_min = np.mean([first_min, second_min], dtype=np.int32)
            average_max = np.mean([first_max, second_max], dtype=np.int32)
            # Complete missing lines
            for i in range(first_index + 1, second_index):
                file.write(f"Row {i} missing\n")
                white_boundaries.append([i, average_min, average_max])

    # To ensure the right order
    white_boundaries.sort(key=lambda x : x[0])


    # 2) Check for absurd values, and correct them
    # Threshold that tells when a value should be considered as an error
    # Here tolerate 7% errors
    PIXEL_THRESHOLD = ncol * 0.07
    # Iteration taking 3 tuples at a time
    for boundaries_index, (first_b, second_b, third_b) in enumerate(
        zip(white_boundaries, white_boundaries[1:], white_boundaries[2:])
    ):

        keys = ['index', 'min', 'max']
        first = dict(zip(keys, first_b))
        second = dict(zip(keys, second_b))
        third = dict(zip(keys, third_b))
        average = {
            'min': np.mean([first['min'], third['min']], dtype=np.int32),
            'max': np.mean([first['max'], third['max']], dtype=np.int32),
        }

        # Check if values of middle row are absurd
        this_error = None
        if abs(average['min'] - second['min']) > PIXEL_THRESHOLD:
            this_error = 'min'
        elif abs(average['max'] - second['max']) > PIXEL_THRESHOLD:
            this_error = 'max'

        if this_error:
            white_boundaries[boundaries_index+1][1 if this_error == 'min' else 2] = average[this_error]
            file.write(f"Row {first['index']} - {second['index']} - {third['index']} " +\
            f"have {this_error} absurd value. " +\
            f"Before : {first[this_error]} - {second[this_error]} - {third[this_error]}. " +\
            f"After : {first[this_error]} - {average[this_error]} - {third[this_error]}\n")


        # OLD CODE
        # first_index, first_min, first_max = first_b
        # second_index, second_min, second_max = second_b
        # third_index, third_min, third_max = third_b

        # average_min_neighbours = np.mean([first_min, third_min], dtype=np.int32)
        # average_max_neighbours = np.mean([first_max, third_max], dtype=np.int32)

        # # Check if values of middle row are absurd
        # if abs(average_min_neighbours - second_min) > PIXEL_THRESHOLD:
        #     white_boundaries[boundaries_index+1][1] = average_min_neighbours
        #     file.write(f"Row {first_index} - {second_index} - {third_index} " +\
        #     f"have minimum absurd value. Before : {first_min} - {second_min} - {third_min}. " +\
        #     f"After : {first_min} - {average_min_neighbours} - {third_min}\n")
        #
        # if abs(average_max_neighbours - second_max) > PIXEL_THRESHOLD:
        #     white_boundaries[boundaries_index+1][2] = average_max_neighbours
        #     file.write(f"Row {first_index} - {second_index} - {third_index} " +\
        #     f"have maximum absurd value. Before : {first_max} - {second_max} - {third_max}. " +\
        #     f"After : {first_max} - {average_max_neighbours} - {third_max}\n")

    # Fill the mask
    for row_index, min_white, max_white in white_boundaries:
        seg_mask[row_index, min_white:max_white+1] = 255

    file.close()
    # Similar to os.stat()
    if file_path.stat().st_size == 0:
        # unlink() from pathlib is similar to os.remove()
        Path.unlink(file_path)

    return seg_mask


def mm_to_imagecoordinates(image, point):
    """Convert the given point location in mm to corresponding row and column indices
    @params:
        image    - Required : image (Pydicom) corresponding to one specific slice
        point    - Required : 1D array containing the x and y coordinates (in mm) of the point
    """
    # This function uses the equation given in the DICOM browser documentation
    # to convert from millimeters to indices (image coordinates).
    # Source : https://dicom.innolitics.com/ciods/ct-image/image-plane/00200032

    # The two equations to solve for i and j are the following :
    # (Xx * Di)*i (Yx * Dj)*j = Px - Sx
    # (Xy * Di)*i (Yy * Dj)*j = Py - Sy

    # All these variables are extracted from following DICOM tags
    IMAGE_POSITION = (0x20,0x32)
    PIXEL_SPACING = (0x28,0x30)
    IMAGE_ORIENTATION = (0x20,0x37)

    Sx, Sy, _Sz = image[IMAGE_POSITION].value
    Di, Dj = image[PIXEL_SPACING].value
    Xx, Xy, _Xz, Yx, Yy, _Yz = image[IMAGE_ORIENTATION].value
    Px, Py = point

    # Equations in matrix form ax = b
    a = np.array([[Xx * Di, Yx * Dj], [Xy * Di, Yy * Dj]])
    b = np.array([Px - Sx, Py - Sy])

    i, j = np.linalg.solve(a, b)

    return [round(i), round(j)]
