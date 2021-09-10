# Glossary

## Biopsy
Medical test, extracting of samples cells  or tissues to determine the presence or extent of a disease.

## MRI (medical resonance imaging) sequence
The MRI is a medical imaging using strong magnetic fields. When atoms are excited/perturbed with a magnetic field, and thet emit an electromagnetic signal with a frequency characteristic of the magnetic field at the nucleus.
A **sequence** is a particular setting of pulse sequences and pulsed field fradients, resulting in a particula image appearance. Examples of different sequences:

- **T2 weighted**, T2 is the spin–spin relaxation time (the time it takes for the magnetic resonance signal to irreversibly decay to 37%). After being excited, atoms tends to relax, and the differences in the decay are captured. The image is built on these differences, tumor appears in white.
- **DWI (diffusion weighted images)**, measures the random Brownian motion of the water molecules within the tissues, tumor appears in white. DWI is caracterized by its **b-value** (The b-value is a factor that reflects the strength and timing of the gradients used to generate diffusion-weighted images. The higher the b-value, the stronger the diffusion effects).
- **ADC (apparent diffusion coefficient)**, is the same as a DWI image, but it has dropped the T2 weighted, tumor appears in black.

MRI can only see soft tissues, but not hard ones.

## Tumors and cancer
A tumor is an abnormal mass of tissue that forms when cells grow and divide more than they should or do not die when they should. (https://www.cancer.gov/publications/dictionaries/cancer-terms/def/tumor).
Cancerous tumors spread into, or invade, nearby tissues and can travel to distant places in the body to form new tumors. (https://www.cancer.gov/about-cancer/understanding/what-is-cancer).
Tumors for the brain and the prostate have well defined boudaries. Tumors for lung has a shape of a spider web, with a central nodule.

## CT (computerized tomography) scans, (tomodensitométrie)
The CT scan is a medical imaging using X-rays. It can see hard tissues (like bones).

## Reference system in anatomy

- **Sagittal**, from left to right (ear to ear)
- **Axial or Transversal**, from up to down (head to feet)
- **Coronal** (or frontal), from front to back (nose to back)

## DICOM (Digital Imaging and Communications in Medicine)
Format/extension for MRI, containing images and metadata (patient ID, bits per channel, ...). Metadata is classified by tags. Tags consist of a group number and an element number in hexadecimal, for example (3006, 00B0). List of all tags : https://exiftool.org/TagNames/DICOM.html

## PACS (Picture archiving and communication system)
System (in the HFR) where we can see the images, make the diagnosis, see the patients, etc...

## Gleason score
Score to grade/classify a prostate cancer according to aggression, by looking the cells under a miscroscope after a biopsy. Goes from 6 (lowest grade cancer) to 10. Cells in prostate are classified in 5 patterns. After a biopsy, the pathologist assign a first grade (from 1 to 5, but pathologists rarely put 1 or 2) to the most predominant pattern, and a second grade to the second most dominant pattern. A score can be for example 3+4 (=7). \
Source : https://www.pcf.org/about-prostate-cancer/diagnosis-staging-prostate-cancer/gleason-score-isup-grade/

## PSA (Prostate specific antigen) score
The PSA is a protein produced by cells in the prostate. One can mesure the level of PSA by directly in a man's blood. A man who has a prostate cancer will have a bigger level of PSA in his blood. A level of PSA between 4 ng/ml and 10 ng/ml can indicate cancer. \
Source : https://www.cancer.gov/types/prostate/psa-fact-sheet

## PIRADS (Prostate Imaging Reporting and Data System) score
Score to put a likelihood of an MRI to contain a tumor. It is an interpretation on the MRI, and not on the actual cells (like the Gleason score with the real cells). It ranges from 1 (almost certainly of absence of cancer) to 5 (cancer presence is very likely), and 3 being a 50% chance of having cancer. We can write several PIRADS scores, if we have more than one tumor. \
Sources : https://www.dredema.com/pi-rads.html et https://sperlingprostatecenter.com/pi-rads-score/

## TNM (tumor, node, metastasis) staging system
Alphanumerical system to stage a prostate cancer. Tumor is divided in 4 stages (T1 to T4). For each stage, letters are added to add information about the cancer. For example, T1b, T3c, T4a, etc...\
Source : https://www.cancerresearchuk.org/about-cancer/prostate-cancer/stages/tnm-staging

## Prostatectomy
Surgical procedure to remove all or a part of the prostate gland. Used to then killed the tumor by radiation.
Source : https://www.mayoclinic.org/tests-procedures/prostatectomy/about/pac-20385198
