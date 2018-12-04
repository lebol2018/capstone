import pandas as pd
import numpy as np
import time
import pickle

bavg = 0

# Function to calculate the RMSE score
def calculate_score(m1, verbose=True):
    '''
    Input: m1 - Either the test or train utility matrix
           m2 - The predictions matrix
           verbose - True/False whether or not to output text during the calculation

    Output: rmse - The calculated Root Mean Squared Error
    '''
    if verbose:
        print("Calculating score...")
        print("Find diff...")

    # First subtract the matrices
    # m1 contains lots if NaNs, meaning we only actually get the diff between the
    # original ratings and the predictions
    diff = np.subtract(m1, bavg)
    print(diff.shape)
    print(m1.shape)

    if verbose:
        print("Done.")
        print("fillna...")

    # Replace NaNs with zeroes
    diff = diff.fillna(0)

    if verbose:
        print("Done.")
        print("Find sqaure of diff...")

    # Find the square of the diffs
    diff = diff*diff

    if verbose:
        print("Done.")
        print("Sum of diff...")

    # Find the sum of the (squared) diffs
    err = np.sum(np.sum(diff))

    if verbose:
        print("Done.")

    # Divide by the number of non-zero elements
    # We need to divide 'err' by the number of original ratings
    if verbose:
        print("Count number of non-zero values...")
    d = diff[diff == 0].count().sum()
    d = diff.shape[0]*diff.shape[1] - d
    mse = err/d
    rmse = np.sqrt(mse)
    return rmse

print("Reading in csv files...")
books = pd.read_csv('books.csv')
ratings = pd.read_csv('ratings.csv')
print("Done.")

print("Load training matrix from file...")
with open('user_ratings_train.dat', 'rb') as fp:
    train_mat = pickle.load(fp)
print("Done.")
print(train_mat.shape)

print("Load test matrix from file...")
with open('user_ratings_test.dat', 'rb') as fp:
    test_mat = pickle.load(fp)
print("Done.")
print(test_mat.shape)

bavg = np.array(list(books.average_rating))

# Calculate MSE taking nans into account
train_rmse = calculate_score(train_mat)
print("RMSE on training set: " + str(train_rmse))
test_rmse = calculate_score(test_mat)
print("RMSE on test set: " + str(test_rmse))
