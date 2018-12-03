import pandas as pd
import numpy as np
import time
import pickle

# Create a utility matrix from a dataframe containing user_id, book_id rating
def create_matrix(df):

    start_time = time.time()

    n_columns = len(df.book_id.unique())
    print("Columns: " + str(n_columns))
    print("Rows: " + str(len(df.user_id.unique())))

    d = {}
    for uid in sorted(df.user_id.unique()):
        d[uid] = [np.nan] * n_columns

    matrix = pd.DataFrame.from_dict(d, orient='index')

    matrix.columns = sorted(df.book_id.unique())

    for index, row in df.iterrows():
        r = int(row['rating'])
        matrix.set_value(row['user_id'], row['book_id'], r)

    elapsed_time = time.time() - start_time
    print ('Execution time: %.1f s' % elapsed_time)

    return matrix

print("Reading in ratings.csv...")
ratings = pd.read_csv('ratings.csv')
print("Done.")
print("Number of ratings: " + str(ratings.shape[0]))
print("\n")


print("Create the ratings matrix...")
um = create_matrix(ratings)
um = um.fillna(0)
print("Done.")

print ("Writing matrix to file...")
with open('user_ratings_matrix.dat', 'wb') as fp:
    pickle.dump(um, fp)
print("Done.")

#exit(0)

print("Split ratings into train and test sets...")
msk = np.random.rand(len(ratings)) < 0.75
ratings_train = ratings[msk]
ratings_test = ratings[~msk]
print("Done.")

print("Create training rating matrix...")
mat_train = create_matrix(ratings_train)
print("Done.")

print("Write training rating matrix to file...")
with open('user_ratings_train.dat', 'wb') as fp:
    pickle.dump(mat_train, fp)
print("Done.")

print("Create test rating matrix...")
mat_test = create_matrix(ratings_test)
print("Done.")


print("Write test rating matrix to file...")
with open('user_ratings_test.dat', 'wb') as fp:
    pickle.dump(mat_test, fp)
print("Done.")
