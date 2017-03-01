from lib.timemachine import TimeMachine
from lib.lastfm import Lastfm

def filter_with(user, filters):
    temp_df = user.library.copy()
    lastfm = user.lastfm
    # limit to timeslice
    temp_df['count'] = lastfm.get_count(temp_df, filters['timeslice'])
    # limit to specified tags
    temp_df = tag_filter(temp_df, filters['tags'])

    keys = list(filters.keys())
    for key in keys:
        if filters[key] is not None:
            params = filters[key]
            method = params[0]
            if method == 'filter_by':
                temp_df = filter_by(temp_df, key, *params[1:])

    return temp_df


def filter_by(df, feature, top_percentage=0.85, reverse=False):
    max = df[feature].values.max()
    if reverse:
        temp_df = df.sort_values(feature, ascending=True)
    else:
        temp_df = df.sort_values(feature, ascending=False)
    limit = 1 - int(len(temp_df) * top_percentage)
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

