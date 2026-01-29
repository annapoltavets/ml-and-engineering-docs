import pandas as pd
import numpy as np

TITLE_TYPE_FILTER = ['movie', 'tvSeries', 'tvMovie', 'tvMiniSeries', 'tvEpisode']
#FILTER_GENRES = ['Animation', 'Game-Show', 'Music', 'Musical', 'News', 'Reality-TV', 'Short', 'Sport', 'Talk-Show', 'Documentary']
FILTER_GENRES = []
START_YEAR = 1927
END_YEAR = 2026
MIN_NUM_VOTES = 100
PARENT_FOLDER = '/Users/apoltavets/anna-apps/ml-and-engineering-docs/ratings/'


class ImdbBaseDataLoader:

    def __init__(self, from_cache=False):
        imdb_base_path = PARENT_FOLDER + 'data/cache/imdb_base.tsv.gz'

        if from_cache:
            print(f"Loading IMDb base data from cache {imdb_base_path}...")
            self.imdb_base = pd.read_csv(imdb_base_path, sep='\t', compression='gzip', low_memory=False)
            self.imdb_base = self.load_my_ratings(self.imdb_base)
        else:
            print("Loading IMDb base data from source files...")
            titles = self.load_titles()
            episodes = self.load_episodes(titles)
            merged_episodes = self.merge_episodes(titles, episodes)
            imdb_base_df = self.transform_genres(merged_episodes)
            self.imdb_base = self.load_my_ratings(imdb_base_df)

            print(f"Saving IMDb base data to cache {imdb_base_path}...")
            self.imdb_base.to_csv(imdb_base_path, compression='gzip', sep='\t', index=False)


    def load_titles(self):
        ratings_path = PARENT_FOLDER + 'data/imdb/title.ratings.tsv.gz'
        basics_path = PARENT_FOLDER + 'data/imdb/title.basics.tsv.gz'

        ratings = pd.read_csv(ratings_path, sep='\t', compression='gzip', low_memory=False)
        basics = pd.read_csv(basics_path, sep='\t', compression='gzip', low_memory=False)
        title_base = pd.merge(ratings, basics, on='tconst', how='inner')

        title_base = title_base[title_base['titleType'].isin(TITLE_TYPE_FILTER)]
        title_base = title_base[title_base['numVotes'] > MIN_NUM_VOTES]

        title_base = title_base[title_base['startYear'] != '\\N']
        title_base['startYear'] = title_base['startYear'].astype('int')
        title_base = title_base[(title_base['startYear'] > START_YEAR) & (title_base['startYear'] < END_YEAR)]
        title_base['endYear'] = title_base['endYear'].where(title_base['endYear'] != '\\N', title_base['startYear'])
        title_base['endYear'] = title_base['endYear'].astype('int')

        title_base['runtimeMinutes'] = title_base['runtimeMinutes'].where(title_base['runtimeMinutes'] != '\\N', 0).astype('int')
        title_base = title_base[((title_base['titleType'] == 'tvEpisode') & (title_base['runtimeMinutes'] < 151)) | (title_base['runtimeMinutes'] == 0) | (title_base['runtimeMinutes'] > 15)]

        title_base['genres'] = title_base['genres'].replace("\\N", np.nan)

        title_base = title_base.loc[title_base.groupby(['primaryTitle', 'startYear'])['numVotes'].idxmax()]

        COLUMN_NAMES = {'averageRating': 'imdb_rating',
                        'numVotes': 'imdb_num_votes',
                        'titleType': 'title_type',
                        'startYear': 'start_year',
                        'endYear': 'end_year',
                        'primaryTitle': 'title',
                        'runtimeMinutes': 'runtime_minutes'}
        title_base = title_base.rename(columns=COLUMN_NAMES)

        title_base = title_base[['tconst',
                                 'imdb_rating',
                                 'imdb_num_votes',
                                 'title_type',
                                 'title',
                                 'start_year',
                                 'end_year',
                                 'runtime_minutes',
                                 'genres']]

        return title_base

    def load_episodes(self, title_base):
        episode_mapping = pd.read_csv(PARENT_FOLDER + 'data/imdb/title.episode.tsv.gz', sep='\t', compression='gzip', low_memory=False)
        episode = pd.merge(episode_mapping, title_base, left_on='parentTconst', right_on='tconst', how='inner')
        episode = episode[episode['parentTconst'].notna()]

        episode = episode.rename(columns={'tconst_x': 'tconst',
                                          'parentTconst': 'tconst_parent',
                                          'title': 'parent_title',
                                          'seasonNumber': 'season',
                                          'episodeNumber': 'episode',
                                          'genres': 'parent_genres'})
        episode = episode[['tconst', 'tconst_parent', 'parent_title', 'season', 'episode', 'parent_genres']]
        return episode

    def merge_episodes(self, title_base, episode):
        merged_base = pd.merge(title_base, episode, left_on='tconst', right_on='tconst', how='left', suffixes=('', '_episode'))

        merged_base['season'] = merged_base['season'].apply(lambda x: '0' if x == '\\N' else x).fillna('0').astype('int')
        merged_base['episode'] = merged_base['episode'].apply(lambda x: '0' if x == '\\N' else x).fillna('0').astype('int')
        merged_base['tconst_parent'] = merged_base['tconst_parent'].fillna('')
        merged_base['parent_title'] = merged_base['parent_title'].fillna('')
        return merged_base

    def transform_genres(self, df):
        df["genres"] = df["genres"].combine_first(df["parent_genres"]).fillna('')
        df = df.drop(['parent_genres'], axis=1)
        df['genres'] = df['genres'].apply(filter_genres_lambda)
        df = df[df['genres'] != 'OUT']

        df['num_genres'] = df['genres'].apply(lambda x: len(x.split(',')) if isinstance(x, str) else 0)

        genres_set = {'Action', 'Adult', 'Adventure', 'Biography', 'Comedy', 'Crime',
                      'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History',
                      'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'}

        for genre in genres_set:
            df[f'is_{genre.lower().replace("-", "_")}'] = df['genres'].apply(lambda x: 1 if isinstance(x, str) and genre in str(x).split(',') else 0)
        return df

    def load_my_ratings(self, titles):
        mdf = pd.read_csv('data/imdb/my_rating.csv')
        mdf = mdf[['Const', 'Your Rating']].rename(columns={'Const': 'tconst', 'Your Rating': 'my_rating'})
        print(f"Loaded {mdf.shape} of my ratings")
        if  'my_rating' in titles.columns:
            titles = titles.drop(['my_rating'], axis=1)
        tdf = titles.merge(mdf, on='tconst', how='left', suffixes=('', '_level1'))
        tdf = tdf.merge(mdf, left_on='tconst_parent', right_on='tconst', how='left', suffixes=('', '_level2'))
        tdf["my_rating"] = tdf["my_rating"].combine_first(tdf["my_rating_level2"]).fillna(0)
        tdf = tdf.drop(['tconst_level2', 'my_rating_level2'], axis=1)
        return tdf


def filter_genres_lambda(genres):
    s = str(genres).split(',')
    for f in FILTER_GENRES:
        if f in s:
            return 'OUT'
    return genres

def encode_title_type_lambda(x):
    if x == 'movie':
        return 0
    elif x == 'tvMovie':
        return 1
    elif x == 'tvSeries':
        return 2
    elif x == 'tvMiniSeries':
        return 3
    elif x == 'tvEpisode':
        return 4
    else:
        return -1


if __name__ == "__main__":
    loader = ImdbBaseDataLoader(from_cache=False)


