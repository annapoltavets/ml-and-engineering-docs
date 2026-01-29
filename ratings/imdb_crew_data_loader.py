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


class ImdbCrewDataLoader:

    def __init__(self, imdb_base, from_cache=False):
        imdbcrew_calc_path = PARENT_FOLDER + 'data/cache/imdb_crew_calc.tsv.gz'

        if from_cache:
            print(f"Loading IMDb base data from cache {imdbcrew_calc_path}...")
            self.crew_calc = pd.read_csv(imdbcrew_calc_path, sep='\t', compression='gzip', low_memory=False)

        else:
            name = pd.read_csv('data/imdb/name.basics.tsv.gz', sep='\t', compression='gzip', low_memory=False)
            crew = pd.read_csv('data/imdb/title.crew.tsv.gz', sep='\t', compression='gzip', low_memory=False)
            crew = imdb_base[['tconst']].merge(crew, on='tconst', how='inner')

            print("Loading names...")
            directors = self.init_crew_load(name, crew, 'directors')
            directors['role'] = 'director'
            writers = self.init_crew_load(name, crew, 'writers')
            writers['role'] = 'writer'
            crew = pd.concat([directors, writers], ignore_index=True)

            self.crew_calc = self.calc_agg(imdb_base, crew)
            print(f"Saving IMDb base data to cache {imdbcrew_calc_path}...")
            self.crew_calc.to_csv(imdbcrew_calc_path, compression='gzip', sep='\t', index=False)


    def init_crew_load(self, name, crew, roles):
        df = crew.copy()
        df['nconst'] = df[roles].apply(lambda x: x.split(','))
        df = df[['tconst', 'nconst']].explode('nconst', ignore_index=True)
        df = pd.merge(df, name, on='nconst', how='inner')

        df = df[['tconst', 'nconst', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession']]

        df = df.rename(columns={'primaryName': f'nconst_name',
                                'birthYear': f'nconst_birth_year',
                                'deathYear': f'nconst_death_year',
                                'primaryProfession': f'nconst_roles'})

        df[f'nconst_birth_year'] = df[f'nconst_birth_year'].apply(lambda x: '0' if x == '\\N' else x).fillna('0').astype('int')
        df[f'nconst_death_year'] = df[f'nconst_death_year'].apply(lambda x: '0' if x == '\\N' else x).fillna('0').astype('int')
        return df

    def calc_agg(self, imdb_base, df_crew):
        df = pd.merge(imdb_base, df_crew, on='tconst', how='inner').drop_duplicates()
        director_title_count = df.groupby(['nconst'])['tconst'].count().rename(f'nconst_title_count')
        directors_num_votes = df.groupby(['nconst'])['imdb_num_votes'].sum().rename(f'nconst_num_votes')
        directors_rating = df.sort_values(by=['nconst', f'nconst_name', 'imdb_rating'], ascending=[True, True, False]).groupby(['nconst', f'nconst_name']).head(3)
        directors_avg_rating = directors_rating.groupby(['nconst', f'nconst_name'])['imdb_rating'].mean().rename(f'nconst_avg_rating')
        directors_avg_my_rating = df.groupby(['nconst', f'nconst_name'])['my_rating'].mean().rename(f'nconst_avg_my_rating')
        agg_df = df.merge(director_title_count, on='nconst', how='left')
        agg_df = agg_df.merge(directors_num_votes, on='nconst', how='left')
        agg_df = agg_df.merge(directors_avg_rating, on='nconst', how='left')
        agg_df = agg_df.merge(directors_avg_my_rating, on='nconst', how='left')
        return agg_df

def main():
    loader = ImdbCrewDataLoader(imdb_base=ImdbBaseDataLoader(from_cache=True).imdb_base, from_cache=False)


if __name__ == "__main__":
    main()