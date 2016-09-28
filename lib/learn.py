import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from sklearn.mixture import GMM
import pandas as pd

# Ideas:
"""
Randomly pull together
"""

df = pd.read_csv('./data.csv')
# grab the song metadata from the csv
X = df.iloc[:, 2:7].values
gmm = GMM(n_components=8, covariance_type='full')
X = X.astype(np.float)
gmm.fit(X)
# the per_component probability
responsibilities = gmm.score_samples(X)[1]
# predicted class label
labels = gmm.predict(X)
labeled_array = []
it = np.nditer(labels, flags=['f_index'])
while not it.finished:
    labeled_array.append([df.iloc[it.index, 0], it[0]])
    it.iternext()
label_df = pd.DataFrame(labeled_array)
label_df.columns = ['track_name', 'cluster_group']
values = label_df.values
df = pd.concat([df, label_df.iloc[:,1]], axis=1)
# try to find where
# print(df[df.iloc])
