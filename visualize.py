from flask import Flask, redirect, request
import requests as http
import json
import uuid
import numpy as np
import pandas as pd
import pprint
import csv
import matplotlib.pyplot as plt
from sklearn.mixture import BayesianGaussianMixture
from lib.spotify import Spotify
from lib.learn import agglomerate_data
from lib.playlist import Playlist

df = pd.read_csv('data.csv')
X = df.iloc[:, 2:4].values

plt.scatter(X[:,0], X[:,1], c='r')
plt.title('Spotify Library Tracks')
plt.xlabel('Danceability')
plt.ylabel('Energy')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.show()

gmm = BayesianGaussianMixture(n_init=1,n_components=15, covariance_type='full', weight_concentration_prior=100,mean_precision_prior=.01, weight_concentration_prior_type='dirichlet_distribution', max_iter=1000)
gmm.fit(X)
xx, yy = np.meshgrid(np.arange(0, 1, .01), np.arange(0, 1, .01))
to_be_plotted = gmm.predict(np.c_[xx.ravel(), yy.ravel()])
to_be_plotted = to_be_plotted.reshape(xx.shape)
fig, ax = plt.subplots()
ax.contourf(xx, yy, to_be_plotted, cmap=plt.cm.Paired)
ax.axis('off')
plt.title('Bayesian Gaussian Mixture Model')
plt.show()

