from sklearn.mixture import BayesianGaussianMixture
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
"""
Take the pandas.DataFrame and cluster the data with GMM
"""
def agglomerate_data(df, components, chosen_features):
    np.set_printoptions(threshold=np.inf)
    df = df.dropna()
    X = df[chosen_features].values
    gmm = BayesianGaussianMixture(n_init=1,n_components=components, covariance_type='full', weight_concentration_prior=100,mean_precision_prior=.01, weight_concentration_prior_type='dirichlet_distribution', max_iter=1000)
    X = X.astype(np.float)
    gmm.fit(X)
    # the per_component probability
    responsibilities = gmm.score_samples(X)[1]
    # predicted class label
    labels = gmm.predict(X)
    labeled_array = []


    for index, value in np.ndenumerate(labels):
        row = []
        for elem in df[chosen_features].iloc[index, :].values.tolist()[0]:
            row.append(elem)
        row.append(value)
        labeled_array.append(row)

    label_df = pd.DataFrame(labeled_array)
    label_df.columns = chosen_features + ['cluster_id']
    return pd.concat([ df[['track_name', 'track_id', 'popularity']], label_df], axis=1)
