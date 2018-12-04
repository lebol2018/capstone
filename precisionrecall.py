import pandas as pd
import numpy as np
import requests
import pickle

n_books = 10000
r_threshold = 0
n_recs = 10


print("Reading in csv files...")
books = pd.read_csv('books.csv')
ratings = pd.read_csv('ratings.csv')
print("Done.")
bavg = np.array(list(books.average_rating))

print ("Read ratings matrix from file...")
with open('user_ratings_matrix.dat', 'rb') as fp:
    ratings_matrix = pickle.load(fp)
print("Done.")
ratings_matrix = pd.DataFrame(ratings_matrix)
print(ratings_matrix.shape)


print ("Read predictions matrix from file...")
with open('predictions_matrix.dat', 'rb') as fp:
    preds = pickle.load(fp)
print("Done.")
preds = pd.DataFrame(preds)
print(preds.shape)

def score(uid):
    '''
    Input: uid - A user id
    Output:
            n - The number of books rated by the user
            r - The number of "relevant" books (books rated higher than the user avg)
            precision - precision@n
            recall - recall@n
    '''
    recs = []

    # Extract all book ids rated above threshold by this users from predictions
    ur = preds.iloc[uid-1].values
#    ur = bavg
    msk = ur > r_threshold
    r = list(ur[msk])
    ids = list(np.nonzero(ur > r_threshold)[0] + 1)
    for i in range(len(r)):
        recs.append((ids[i], r[i]))

    # Sort recommendations by rating
    sorted_recs = sorted(recs, key=lambda tup: tup[1], reverse=True)

    # Extract only the book ids
    recs = [x[0] for x in sorted_recs]

    # How many books has the user rated
    d = np.array(ratings_matrix.iloc[uid-1])
    r = np.argwhere(d > 0) + 1
    books_rated = [x[0] for x in r]
    n_rated = len(books_rated)
#    print("Books rated: " + str(n_rated))

    uavg = d[d > 0].mean()
#    print("Average rating: " + str(uavg))
    r = np.argwhere(d > uavg) + 1
    relevant_books = [x[0] for x in r]
    n_relevant = len(relevant_books)
#    print("Relevant books: " + str(n_relevant))

    recs = recs[:50]
    n_recs = len(recs)
#    print("Recommendations: " + str(n_recs))


    rel = list(set(recs).intersection(set(relevant_books)))
    n_rec_rel = len(rel)
#    print("Recommended, relevant books: " + str(n_rec_rel))

    precision = n_rec_rel / n_recs
    recall = n_rec_rel / n_relevant

#    print("Precision: " + str(precision))
#    print("Recall: " + str(recall))

    return n_rated, n_relevant, precision, recall

total_precision = 0
total_recall = 0
n_users = 100

for uid in range(1, n_users + 1):
    n, r, prec, rec = score(uid)
    total_precision += prec
    total_recall += rec

avg_prec = total_precision / n_users
avg_rec = total_recall / n_users

print("Precision: " + str(avg_prec))
print("Recall: " + str(avg_rec))
