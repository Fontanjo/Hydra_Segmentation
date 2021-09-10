# 1. General, 17 August 2021

## Material
Read the 2 thesis and ask questions

## Thesis work
MRI (variation in density, slice of images, 3 sequences (one in each dimension) to have the same resolution in the 3 axes, dimensionality more than 3 because of the time and the type of scan, so very difficult to dimensionality) Data processing, 1000 patients will need to be anonymized, work with radiologist, make an automatic tool to:
1. Segmentation (perimeter/boundary, dimensionality)
2. Cancer diagnosis (yes or no malignant mass (piece of tissue), with 1 neuron with prob)
3. Location (x,y mass center, with two neurons)
4. Level of certitude

There are the labels for SL, **biopsy** (control to be sure by taking tissue inside a patient)

## Bureaucracy
Sign a paper after the work,supervisor Cudré-Mauroux,
**14:00 24th august on the parking main entrance of the HFR**

## Schedule
Weekly meeting with Cuccu, and in HFR, maternal, 30min weekly meeting (on Thursday 13:00) with Cuccu to be consistent and short, meeting for the data and the whole project

## Tools
* Latex + template (overleaf good for more people, google docs for the text, otherwise in local)
* Python + Jupiter
* Linux mint distribution with cinnamon (work locally, but access to other servers, or on computers of the HFR)
* GitHub
* Coding env
* Lists (todo list (prioritization) and wish list (becoming a researcher)) (markdown), ATOM or sublime text

**Meeting every Thursday between 13:00pm – 13:30pm**

# 26 August 2021
We speak a little bit about the first version of the renamer.py. Mr. Cuccu tell me that I needed to learn some useful shortcuts for ATOM, place the comments in the code in the line above, try to learn the English keyboard.

I need also to read again my notes about the technical stuff for the thesis, that means the medical stuff, in link with the MRI, prostate, DICOM, and the related libraries in Python. I need also to install a jupyter notebook, it is easier to see the things (like dicoms).

# 2 September 2021
Today I show Mr. Cuccu my jupyter notebook, and what can Pydicom do in general. Thesis cancelled ?

# 7 September 2021
Discussion about what is going on next for the thesis.

Reason of collaboration with HFR : patient data -> black box -> diagnosis (can be either binary (yes no), localization or segmentation). Requires SL, so aggregation of patient data (MRIs, personal data, blood analysis, CF **cancer images archive**) and correct diagnosis.

**Black box** : use deep learning (SL), deep NN, feature extraction with convolution, decision making on top (fully connected NN)

We take MRIs (for the moment only DWI, cropped and rescaled with the tumor in the center, and data augmentation (aritificial data by modify the orientation or the zoom of existing images), and also normalized) and their corresponding diagnosis. Problem of deep NN is the vanishing gradient, we need a lot of data. Idea : do a feature extractor that extracts features (it is trained with lung, brain or prostate together), and another network that is the decision maker and output the diagnosis (3 FE for each of the 3 different organs).

There are two version of the current model.

Basic Hydra : one body (FE) and many heads (DM). Train : initiation, train DM by freezing the FE, train end to end by unfreezing the FE, each of the organ one after the other sequentially. We then try to train in another order (first the prostate, brain then lung).

P-hydra : P for parallel training : initiation, 1 batch end to end for each organs, and loop for all epochs. Batch because of the imbalanced size of the three datasets, it is not a problem if the dataset is the same, we do batches with random images in random order, so we can do more batches with the same dataset. Warning to "cheat". Don't train the NN with only one organ for too long, it won't scale well. Goal of p-hydra is to make the FE as generic as possible, by mixing the datasets.

**Possible directions of the thesis**
- Inputs: use different sequences, automate preprocessing (data augmentation, cropping and rescaling = preprocessing), 3D convolution (taking hydra and adjust the code to convolution in 3D), high-dimentional convolution, different datasets.
- Targets: localization and segmentation, new datasets, find datasets that have some diagnosis published, with the settings specified, and find cross references between the dataset and the results.

1. **Automatic preprocessing**, preprocess a new dataset, automate the preprocessing of the data, and compare results by the number of the dataset.
2. **3D convolution**, 2D on 3 channels, implementation of the 2D convolve in tensorflow accepts 3 channels (RGB), has better result because we input 3 images (for example ADC, DWI and T2W). 2D convolution accept 3 channels. TODO : see how the imaged are generated, rerun to generated, and finally that load 3D images, and then modify the model to take 3D in input, and compare the performance from the base results (in publications).
3. **Segmentation**, dataprocessing, modify the model for segmentation. Download new dataset that have segmentation (work that have already been published) to have a reference performance, do the processing, change the model to do segmentation, and make the DM make the decision from binary to segmentation.

Goal : produce results and compare with publications

**TODO** for next week 16 september:
- Study the preprocessing script
- Study how 2D convolution works (2D conv function in tensorflow keras or pytorch, or 3Dconv function)
- Search cancer imaging archive (how to find papers, how to download the datasets)
- Find dataset that has segmentation (possibly)
- Download dataset, run the script to preprocess data, and find the same preprocessed data as in the hydra work
- See the three propositions (not sequentially)
- Send an email if needed
- Find the code for hydra


## Defense of bachelor Thesis (Jonas)
Structure of the oral presentation :
- Talk about motivation of the thesis
- Problem definition
- Theory/background for the thesis (some graphs, formulas, some technical stuff)
- Experiments (datasets, starting point)
- Results of the experiments
- Conclusion about the Experiments
- General conclusion of the Thesis

Be prepared to answer some questions, or some following applications. There is also a little discussion about the work, what can be done further or what can have been changed to be improved.
