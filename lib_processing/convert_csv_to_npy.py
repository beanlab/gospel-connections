from pathlib import Path
import numpy as np

def main():
    data_path = Path('../data').absolute().resolve()

    # Define this variable for the specific directory to convert
    main_directory = data_path / 'embeddings' / 'w016_i004' / 'scriptures'

    # Search through all files in entire directory
    for path in main_directory.rglob("*.csv"):
        print('Processing: ', path)
        # for each csv file, load it, and save as npy in the exact same place
        # Load csv
        data = np.genfromtxt(path, delimiter=',')

        new_path = path.with_suffix('.npy')
        # Save as npy file
        np.save(new_path, data)

        # delete old path
        path.unlink()
        #print(new_path)

if __name__ == '__main__':
    main()