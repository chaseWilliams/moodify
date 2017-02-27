from lib.timemachine import TimeMachine
from lib.lastfm import Lastfm

def make_filters():
    pass

def filter_by(df, feature, top_percentage, reverse=False):
    max = df[feature].values.max()
    if neglected:
        temp_df = df.sort_values(feature, ascending=True)
    else:
        temp_df = df.sort_values(feature, ascending=False)
    limit = 1 - int(len(temp_df) * top_percentage)
    return temp_df.iloc[0:limit, :]

def filter_in_range(df, feature, start, stop):
    truth = (df[feature] >= start) & (df[feature] <= stop)
    return df[truth]

def tag_filter(df, genre):
    truth_arr = [False] * len(df)
    for index, genres in enumerate(df['genres']):
        genres = genres.split(',')
        if genre in genres:
            truth_arr[index] = True
    return df[truth_arr]

