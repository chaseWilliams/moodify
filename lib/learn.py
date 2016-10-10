from sklearn.mixture import GMM
import numpy as np
import pandas as pd
"""
Take the pandas.DataFrame and cluster the data with GMM
"""
def agglomerate_data(df, components):
    # grab the song metadata from the csv
    X = df.iloc[:, 2:4].values
    gmm = GMM(n_components=components, covariance_type='diagonal')
    X = X.astype(np.float)
    gmm.fit(X)
    # the per_component probability
    responsibilities = gmm.score_samples(X)[1]
    # predicted class label
    labels = gmm.predict(X)
    labeled_array = []
    #it = np.nditer(labels)
    #while not it.finished:
    #    labeled_array.append([df.iloc[it.index, 0], it[0]])
    #    it.iternext()
    for index, value in np.ndenumerate(labels):
        row = []
        for elem in df.iloc[index, 0:4].values.tolist()[0]:
            row.append(elem)
        row.append(value)
        labeled_array.append(row)

    label_df = pd.DataFrame(labeled_array)
    print(label_df)
    label_df.columns = ['track_name', 'track_id', 'Danceability', 'Energy', 'cluster_id']
    return label_df

#df = pd.read_csv('./data.csv')
#agglomerate_data(df, 8)
