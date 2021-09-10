# Notes about dataset and their processing
## Prostate
For the prostate, the dataset is taken from the SPIE-AAPM-NCI PROSTATEx Challenge dataset. Images that are kept are only in T2W, DWI (with different *b-value*, but performance is better with the highest *b-value*) and ADC greyscale. Images under the transverse plane are prefered, because the tumor is more visible within this plane. The prostate processing is split into two parts : preprocessing and augmentation.

Prostate processing :
- DICOM to NumPy arrays (and also classification yes/no)
- Resampling to the same resolution
- Cropping 130x130px patch, and resizing to 65x65px using bicubic interpolation
- Normalization, based on the Z-score. Mean and standard deviation are taken only from the same sequence of the same patient (for example all DWI of a specific patient)
- Stacking, putting each single image (greyscale) into a single array, as different channels. Resulting in images containing 3 greyscaled channels. The lesion is then visible in the same area over the 3 channels. If not stacking, results are awful because of the color (tumor is white in DWI and black in ADC for example)
- Augmentation, by -20° to 20° rotations, horizontal and vertical flipping. To have more data and to solve the class (yes/no) imbalanced size problem.

To test the processing, a red dot is placed on the full image, and the image is runned in the processing script. This red dot should be in the center of the image, the images contain the exact same tissue, they are not rotated/shifted/flipped, and the lesion is visible to the naked eye.

## Lung
Images taken from the SPIE-AAPM Lung CT Challenge dataset. This dataset has two subdatasets, but were merged for training (70 patients in total). There are more than two labels for this dataset. "Malignant" and "Primary lung cancer" are considered as positive, and "benign" and "benign nodule" as negative. The lung processing is arranged in the same way as the prostate. All images have already the same resolution. Specificity of a lung tumor is its shape. For lung it has a spider web with a central nodule shape, as prostate or brain have more well defined boundaries. So we need a larger patch size.

Lung processing:
- DICOM to NumPy arrays
- Normalization ?
- Cropping 85x85px patch (1/6 of the original image), and resizing to 65x65px using bicubic interpolation
- Augmentation (for class imbalance problem)

## Brain
Images taken from the Kaggle "Brain MRI Images for Brain Tumor Detection" dataset. Comes from the Kaggle website (and not from a medical authority). They are classified in two folders, one with cancerous tumors, and another without tumor or a non-canceours tumor. Images with extremely low quality were removed, as well as disturbing objects added by humans (like arrows or markers). A ground truth CSV had to be created manually, containing patientID, nodule center position, findingID (if the patient has more tumors), diagnosis (false/true). Most of the image were in JPG (the few PNG are manually converted).

Brain processing:
- JPG to NumPy arrays: 3 channels to 1 channel conversion
- Normalization
- Cropping using 1/4 x 2/7 patch (fraction of the image size), and resizing to 65x65px using bicubic interpolation
