import numpy as np

def cos_sim(data_1, data_2):
    return np.dot(data_1, data_2.transpose())/(np.linalg.norm(data_1)*np.linalg.norm(data_2.transpose(), axis=0))