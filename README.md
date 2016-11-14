# Moodify
A project that takes a user's Spotify library and uses unsupervised learning to break it up into different playlists that each have a certain "mood" with it.

## Song Partition
Moodify uses a GMM (Gaussian Mixture Model) to analyze the differences between the songs. It works by using a weighted sum of Gaussian components, where each component is essentially a k-means subpopulation of the total dataset. It's established in a Bayesian setting, which means that the initial conditions are random and the EM (Expectation-Maximization). The hyperparameters are set as to force the algorithm to subdivide massive clusters of songs, as songs typically agglomerate around a certain node (around .8 - .8 Danceability and Energy).

## The Server
### Front End Pages
Moodify has a landing page available at `/begin`. Clicking on 'Harness the Power of Moodify' sends the user through the OAuth 2 authentication using the `/authenticate` endpoint, and after the user is authenticated and the app has the proper token it goes ahead and partitions the song library. When that is done, the user is redirected to the callback endpoint, where in later updates they can control what is saved to their library and fine-tune the playlists, as well as get a general overview of what the new playlists look like and see some statistics about their library.

## The REST Endpoint
Moodify has the endpoint at `/retrieve` that allows users to hit the Redis database and get the results of the data processing that Moodify does. A typical result of hitting the endpoint looks like:
``` json
{
  "status": "ok",
  "contents": [
    [
      {
        "Tempo": "145.022",
        "Energy": "0.675",
        "Danceability": "0.479",
        "track_id": "2KlZexJjJPuNWcN5uAG1GU",
        "cluster_id": 0,
        "Valence": "0.18",
        "track_name": "Gold (feat. Yuna)",
        "Acousticness": "0.0319"
      }
    ]
  ]
}
```
The endpoint takes two query parameters: one is called `uid`, the other `playlists`. `uid` is the Spotify username of the user's data you want to access, and `playlists` is a comma separated list of the playlist ids you want to access. So an example API hit would be `/retrieve?uid=bornofawesomeness&playlists=0`.
