import numpy as np
from scipy.spatial.distance import cdist

def cos_sim(data_1, data_2):
    return np.dot(data_1, data_2.transpose())/(np.linalg.norm(data_1, axis=1, keepdims=True)*np.linalg.norm(data_2.transpose(), axis=0, keepdims=True))

# Alternative approach using scipy, this is supposedly slower
def cos_sim_scipy(data_1, data_2):
    return 1 - cdist(data_1, data_2, metric='cosine')  