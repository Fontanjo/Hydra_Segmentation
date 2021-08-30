# 1. General, 24 August 2021

## Data
All data is currently on disk and is encrypted for safety. All data is in DICOM format and is yet exported. There are DICOM folders with all the MRI slices inside for example. There are many variations and inconsistancies.

They use T2W (initial image, nice contour means tumor) -> processing -> DWI (like a drop in the water, white = tumor) or/and ADC (black = tumor)

DWI : meausure on the time, diffusion is like linear, and can calculate the diffusion

A patient can have more MRIs, which contain more series (like T1, T2W, DWI), patient will have ID.

## Prostate and theory
Three principal zones (Peripheral Zone PZ, transition zone and central zone (less important ?)). Cancer will be more likely located in the PZ.
The MRI helps to make/locate for a better biopsy.
Biopsy is harder with prosthesis.

## Cancer detection and further steps
To detect cancer, first we make a blood test (PSA test). Then we send the patient to an MRI. If the PIRADS score is high, we make a biopsy (and not prostatectomy), MRI helps to locate the likely tumor, and ultrasound (like for echography) is used to guide the needle used for the biopsy.

## TODO:
- Install a software to read DICOM
- Make a program that renames name of the patient + more MRI + different series (multiples sensors, with the given sequence name, accesing in the DICOM metadata)
- Learn and read aboud Pydicom
- (Make a program to save location data from the image (like clicking or contouring), (like SIEMENS Healthineers), labels are for example contour or location to draw with the pen.)

## PYDICOM
Python Library for DICOM files.
