from torch.utils.data import DataLoader
from torch.utils.data import Dataset
import os
import pandas as pd
import numpy as np


class MedicalImageDataset(Dataset):
    def __init__(self, dataset_dir, labels_csv):
        """
        Args:
            - dataset_dir: path to the dataset directory
            - labels_csv: path to the csv file containing the diagnosis
        """

        self.labels_df = pd.read_csv(labels_csv)
        self.dataset_dir = dataset_dir

        # Check that dataset_dir is a directory
        assert os.path.isdir(self.dataset_dir), "dataset_dir is not a directory"

        # Check that the size of the dataset and the csv file are equal
        # print(len(os.listdir(self.dataset_dir)))
        # assert len(os.listdir(self.dataset_dir)) == len(self.labels_df), "Cannot create dataset"

    # def create_iterator:
    #     # For each row in the csv
    #     for nrow, slice_data in self.labels_df.iterrows():
    #         patient_id = slice_data['PatientID']
    #         patient_path = os.join(self.dataset_dir, patient_id)
    #         # Iterate over all visits for a patient
    #         for visit in os.listdir(patient_path):
    #             visit_path = os.join(patient_path, visit)
    #             # Iterate over all series
    #             for serie in os.listdir(visit_path):
    #


    def __len__(self):
        return len(self.labels_df)

    def __getitem__(self, index):
        # Check that the index exists
        # assert self.labels_df.iloc[index, 0] in os.listdir(self.dataset_dir), "Patient not found"
        patient_path = os.path.join(self.dataset_dir, self.labels_df.iloc[index, 0])
        patient_path = np.array(patient_path)
        labels = self.labels_df.iloc[index, :]
        labels = labels.to_numpy()
        item = np.append(patient_path, labels)
        return item



def train_val_test_split(dataset_dir, labels_csv, split_train, split_test):
    """
    Description: Split the dataset in train, test and optionaly validation sets.
    Args:
        - dataset_dir: directory of the dataset to split
        - split_train: percentage of the dataset used as training set
        - split_test: percentage of the dataset used as test set
    Returns:
        Three lists containing the path to the patient and the row in the labels dataframe
    """

    assert split_train + split_test <= 1.0, "Wrong values for splitting"

    # Create a new instance of MedicalImageDataset
    med_dataset = MedicalImageDataset(dataset_dir, labels_csv)

    # dataset_path = Path(dataset_dir)

    # Compute the split_validation (can be 0)
    split_validation = 1 - split_train - split_test

    # Load the dataset in DataLoader
    # dataset_dataloader = DataLoader(med_dataset)

    # Get number of elements and compute size of the different sets
    # n_elements = len(dataset_dataloader)
    n_elements = len(med_dataset)
    n_train = round(n_elements * split_train)
    n_test = round(n_elements * split_test)
    n_validation = n_elements - n_train - n_test
    assert n_train + n_validation + n_test == n_elements, "Problem with size of the sets"

    print(n_elements, n_train, n_test, n_validation)

    # Create the three lists containing the data splitted
    train_list = [med_dataset.__getitem__(i) for i in range(0, n_train)]
    test_list = [med_dataset.__getitem__(i) for i in range(n_train, n_train + n_test)]
    validation_list = [med_dataset.__getitem__(i) for i in range(n_train + n_test, n_elements)]

    print(train_list[1][0]) # To get the path
    # print(next(iter(DataLoader(test_list, batch_size=1))))
    print(train_list)

train_val_test_split('/home/christophe/Desktop/test', '/home/christophe/Desktop/test.csv', 0.7, 0.2)
