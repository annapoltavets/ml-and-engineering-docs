import pandas as pd
import numpy as np

from ratings.imdb_base_data_loader import ImdbBaseDataLoader

TITLE_TYPE_FILTER = ['movie', 'tvSeries', 'tvMovie', 'tvMiniSeries', 'tvEpisode']
#FILTER_GENRES = ['Animation', 'Game-Show', 'Music', 'Musical', 'News', 'Reality-TV', 'Short', 'Sport', 'Talk-Show', 'Documentary']
FILTER_GENRES = []
START_YEAR = 1927
END_YEAR = 2026
MIN_NUM_VOTES = 100
PARENT_FOLDER = '/Users/apoltavets/anna-apps/ml-and-engineering-docs/ratings/'
imdbcrew_calc_path = PARENT_FOLDER + 'data/cache/imdb_principals_details.tsv.gz'
principal_path = PARENT_FOLDER + 'data/imdb/title.principals.tsv.gz'
name_path = PARENT_FOLDER + 'data/imdb/name.basics.tsv.gz'


class ImdbPrincipalDataLoader:

    def __init__(self, imdb_base, from_cache=False):
        if from_cache:
            print(f"Loading IMDb base data from cache {imdbcrew_calc_path}...")
            self.crew_calc = pd.read_csv(imdbcrew_calc_path, sep='\t', compression='gzip', low_memory=False)
        else:
            p = pd.read_csv(principal_path, sep='\t', compression='gzip', low_memory=False)
            name = self.load_names()
            df = imdb_base.merge(p, on='tconst', how='inner')
            self.principals = df.merge(name, on='nconst', how='inner')
            self.principals.to_csv(imdbcrew_calc_path, sep='\t', compression='gzip', index=False)

    def load_names(self):
        name = pd.read_csv(name_path, sep='\t', compression='gzip', low_memory=False)
        name = name[['nconst', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession']]
        name = name.rename(columns={'primaryName': f'nconst_name',
                                    'birthYear': f'nconst_birth_year',
                                    'deathYear': f'nconst_death_year',
                                    'primaryProfession': f'nconst_roles'})
        name[f'nconst_birth_year'] = name[f'nconst_birth_year'].apply(lambda x: '0' if x == '\\N' else x).fillna('0').astype('int')
        name[f'nconst_death_year'] = name[f'nconst_death_year'].apply(lambda x: '0' if x == '\\N' else x).fillna('0').astype('int')
        return name