import pydicom
import numpy as np


def create_segmentation_mask(image, contour_data):
    """Get normalized NumPy array segmentation from DICOM file and contour data
    @params:
        image          - Required : image (Pydicom) corresponding to one specific slice
        contour_data   - Required : 2D array containing contours points of the segmentation
    """
    # Get the number of rows and columns of the image
    nrow = image.Rows
    ncol = image.Columns

    # Initialization
    seg_mask = np.zeros((nrow, ncol))

    # Iterate over all points of the contour data
    for point in contour_data:
        # Convert the point into indexes
        j, i = mm_to_indices(image, point)
        # Set these indexes to a white pixel (= draw the contour)
        seg_mask[j][i] = 255

    # Iterate over rows in the segmentation mask
    for row in seg_mask:
        # Get indices of the white pixels
        # Source : https://stackoverflow.com/questions/34126230/getting-indices-of-a-specific-value-in-numpy-array
        # TODO : Search max and min index where there is white, then iterate over each between lines and draw the white line (if no boundaries, get average of boundaries of the neighbourgs)
        indices = np.argwhere(row == 255).flatten()
        #Iterate over the indices
        for i in range(len(indices)-1):
            # Get two white pixel boundary
            first = indices[i]
            second = indices[i+1]
            # Use slicing to fill white pixel inside the contour
            row[first:second+1] = 255

    return seg_mask


def mm_to_indices(image, point):
    """Convert the given point location in mm to corresponding row and column indices
    @params:
        image    - Required : image (Pydicom) corresponding to one specific slice
        point    - Required : 1D array containing the x and y coordinates (in mm) of the point
    """
    # TODO: more comment from the documentation
    # Get the postition of the upper left pixel (in mm) (Image position tag)
    Sx, Sy, _ = image[0x20,0x32].value

    # Get the pixel spacing
    Di, Dj = image[0x28,0x30].value

    # Get the image orientation
    Xx, Xy, _, Yx, Yy, _ = image[0x20,0x37].value

    # Get the point coodinates
    Px, Py = point

    # Construct the matrix to compute the row and column index
    a = np.array([[Xx * Di, Yx * Dj], [Xy * Di, Yy * Dj]])
    b = np.array([Px - Sx, Py - Sy])

    # Compute the row and column index
    # Careful, i is the column index, and j is the row index
    i, j = np.linalg.solve(a, b)

    return [round(j), round(i)]
