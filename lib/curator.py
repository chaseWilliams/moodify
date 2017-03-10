from lib.timemachine import TimeMachine
from lib.lastfm import Lastfm
import pandas as pd

def filter_with(user, filters):
    temp_df = user.library.copy()
    lastfm = user.lastfm
    # limit to timeslice
    if filters['timeslice'] is not None:
        temp_df['count'] = lastfm.get_count(temp_df, filters['timeslice'])
        del filters['timeslice']
    # limit to specified tags
    if filters['tags'] is not None:
        temp_df = tag_filter(temp_df, filters['tags'])
        del filters['tags']
        
    potentials = []
    keys = list(filters.keys())
    for key in keys:
        if filters[key] is not None:
            params = filters[key]
            method = params[0]
            if len(params) == 2:
                method_params = params[1]
            else:
                method_params = {}
            if method == 'filter_by':
                result = filter_by(temp_df, key, **method_params)
            if method == 'filter_in_range':
                result = filter_in_range(temp_df, key, **method_params)
            potentials.append(result)
    for potential in potentials:
        temp_df = pd.merge(temp_df, potential)
    return temp_df


def filter_by(df, feature, percentage=0.60, reverse=False):
    max = df[feature].values.max()
    if reverse:
        temp_df = df.sort_values(feature, ascending=True)
    else:
        temp_df = df.sort_values(feature, ascending=False)
    limit = 1 - int(len(temp_df) * percentage)
    return temp_df.iloc[0:limit, :]

def filter_in_range(df, feature, start, stop):
    truth = (df[feature] >= start) & (df[feature] <= stop)
    return df[truth]

def tag_filter(df, genres):
    truth_arr = [False] * len(df)
    for index, track_genres in enumerate(df['genres']):
        track_genres = track_genres.split(',')
        for genre in genres:
            for track_genre in track_genres:
                if genre == track_genre:
                    truth_arr[index] = True
    return df[truth_arr]

