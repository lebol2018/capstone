import pandas as pd
import numpy as np
import time
import pickle
import math
import random

print("Reading in csv files...")
books = pd.read_csv('books.csv')
ratings = pd.read_csv('ratings.csv')
print("Done.")

print("Number of books:" + str(books.shape[0]))
print("Number of ratings: " + str(ratings.shape[0]))
print("\n\n")

# Find the global average rating across all books_found
gavg = round(books.average_rating.mean(), 3)
print("Average book rating: " + str(gavg))

# Find the variance of the average rating
va = books.average_rating.var()
print("Average rating variance: " + str(va))

# Find the average rating per user ("User bias")
print("Calculating user bias...")
uavg = ratings.groupby('user_id').rating.mean()
user_bias = uavg - gavg
print("Done.")

# Create a vector of average ratings per book
bavg = np.array(list(books.average_rating))

print("Read training matrix from file...")
with open('user_ratings_train.dat', 'rb') as fp:
    training_matrix = pickle.load(fp)
print("Done.")
print(training_matrix.shape)



# Impute missing values
print("Impute missing values...")

# impute only the nans
impute = lambda x, y: np.where(np.isnan(x), y, x)

counter = 0
start_time = time.time()

for uid in training_matrix.index:
    counter += 1
    if (counter % 10000) == 0:
        print(counter)
        elapsed_time = time.time() - start_time
        print ('Execution time: %.1f s' % elapsed_time)
        start_time = time.time()

#    1. Average book rating
#    imputed_values = bavg

#    2. Average book rating plus user bias
    imputed_values = np.clip(user_bias[uid] + bavg, 1.0, 5.0)

#    3. Random values between 1 and 5
#    imputed_values = np.random.randint(1,6, books.shape[0])

#   4. "Simon Funk's formula"
#    ub = training_matrix.loc[uid]
#    vb = ub.var()
#    k = vb/va
#    imputed_values = (k*gavg + ub.sum()) / (k + ub.count())


    training_matrix.loc[uid] = impute(training_matrix.loc[uid], imputed_values)

print("Done.")

print("Write imputed training rating matrix to file...")
with open('user_ratings_train_imputed.dat', 'wb') as fp:
    pickle.dump(training_matrix, fp)
print("Done.")
