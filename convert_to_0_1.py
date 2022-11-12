import numpy as np
import os

root_folder = "./test_folder"

def main():
    modified_files = 0
    maintained_files = 0

    # Recursively explore all subfolders
    for (root, dirs, files) in os.walk(root_folder, topdown=True):
        # Act on each npy file
        for file in [f for f in files if f.endswith(".npy")]:
            # Load file
            ary = np.load(root + '/' + file)
            # Check max and min value
            max_val, min_val = np.max(ary), np.min(ary)
            # Convert to [0,1] if necessary
            if max_val > 1:
                ary = ary / 255
                modified_files += 1
                np.save(root + '/' + file, ary)
            else:
                maintained_files += 1
    print(f"Files modified: {modified_files}")
    print(f"Files maintained: {maintained_files}")




if __name__ == "__main__":
    main()
