
"""
Take the pandas.DataFrame and cluster the data with GMM
"""
def agglomerate_data(df, components):
    # grab the song metadata from the csv
    X = df.iloc[:, 2:6].values
    gmm = GMM(n_components=components, covariance_type='full')
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
        for elem in df.iloc[index, 0:6].values.tolist()[0]:
            row.append(elem)
        row.append(value)
        labeled_array.append(row)

    label_df = pd.DataFrame(labeled_array)
    label_df.columns = ['track_name', 'track_id', 'Danceability', 'Energy', 'Acousticness', 'Valence', 'cluster_id']
    print(label_df.tail())
    return label_df

#df = pd.read_csv('./data.csv')
#agglomerate_data(df, 8)