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
X = df.iloc[:,1].values
gmm = GMM(n_components=8, covariance_type='full')
X = X.astype(np.float)
gmm.fit(X)
for index, sample in df.iterrows():
    print(gmm.predict(sample))