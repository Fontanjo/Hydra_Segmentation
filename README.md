# Pre-Processing Segmentation Datasets for the Hydra Framework

Author: Christophe Broillet

## Abstract
Early cancer detection is a crucial point nowadays to save human lives. Computer aided diagnosis (CAD) systems, which use machine learning techniques, can help radiologists to detect the very first stages of cancer, but also to locate and segment malignant tumors in medical images. Deep learning models, such as convolutional neural networks, are today useful and powerful for computer vision, which makes them the perfect candidates for CAD systems. However, these models require a lot of data, which is often difficult to obtain in the medical field, because of privacy issues. This work focuses on addressing the data scarcity by preprocessing new datasets to an existing computer aided diagnosis system, namely the Hydra framework, while adding the segmentation task to this CAD system. The new datasets contain CT or PET scans of the lungs, and the head and neck, but also ultrasounds of the breast. The preprocessing of the datasets are shown and explained, and are also provided in three new scripts. These datasets are ready to be used in a segmentation task. This task is useful for radiologists, as it shows precisely where the tumors are located, and gives information about their shape. This work develops a new module that creates segmentation masks of medical images, given the cloud of points that contour the tumor. After using this module, the datasets contain the medical images (inputs) and the segmentation masks (labels). The Hydra framework is now ready to train the segmentation task in a supervised learning manner.

## Repository description
The folder *preprocessing_scripts* contains the preprocessing scripts for three datasets. These scripts preprocess the data before the Hydra model uses it. The scripts are separated for each dataset. The *segmentation_mask* module, that creates segmentation masks given the list of points that contour tumors, is available and used in two datasets.

The *Pipfile* and *Pipfile.lock* are here to install a virtual environment on a new machine that wants to run these scripts.

The original publication of this work is available [here](https://exascale.info/assets/pdf/students/2022_BSc_Christophe_Broillet.pdf) or in this [repository](https://github.com/ChristopheBroillet/bachelor_thesis).
