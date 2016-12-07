from sklearn.mixture import BayesianGaussianMixture
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
"""
Take the pandas.DataFrame and cluster the data with GMM
"""
def agglomerate_data(df, components):
    np.set_printoptions(threshold=np.inf)
    X = df.iloc[:, 2:-1].values
    gmm = BayesianGaussianMixture(n_init=1,n_components=components, covariance_type='full', weight_concentration_prior=100,mean_precision_prior=.01, weight_concentration_prior_type='dirichlet_distribution', max_iter=1000)
    X = X.astype(np.float)
    X = X[~np.isnan(X).any(axis=1)]
    gmm.fit(X)
    # the per_component probability
    responsibilities = gmm.score_samples(X)[1]
    # predicted class label
    labels = gmm.predict(X)
    labeled_array = []


    for index, value in np.ndenumerate(labels):
        row = []
        for elem in df.iloc[index, :].values.tolist()[0]:
            row.append(elem)
        row.append(value)
        labeled_array.append(row)

    label_df = pd.DataFrame(labeled_array)
    label_df.columns = ['track_name', 'track_id', 'Danceability', 'Energy', 'Acousticness', 'Valence', 'Tempo', 'cluster_id']
    return label_df

#df = pd.read_csv('./data.csv')
#agglomerate_data(df, 8)
