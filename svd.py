import pandas as pd
import numpy as np
import time
import pickle
import scipy.sparse
import scipy.sparse.linalg
from sparsesvd import sparsesvd

svd_factors = 20

print("Loading training matrix from file...")
with open('user_ratings_train_imputed.dat', 'rb') as fp:
    matrix = pickle.load(fp)
print("matrix size:")
print(matrix.shape)

print("\n")

start_time = time.time()
print("Fit SVD on the ratings matrix...")
smat = scipy.sparse.csc_matrix(matrix)
u, s, vt = sparsesvd(smat, svd_factors)
print("Done.")
elapsed_time = time.time() - start_time
print ('Execution time: %.1f s' % elapsed_time)

print("u has shape: " + str(u.shape))
print("s has shape: " + str(s.shape))
print("vt has shape: " + str(vt.shape))
print("\n\n")
print("Storing SVD arrays...")

print("Creating pickle file for u...")
with open('u.dat', 'wb') as fp:
    pickle.dump(u, fp)
print("Done.")

print("Creating pickle file for s...")
with open('s.dat', 'wb') as fp:
    pickle.dump(s, fp)
print("Done.")

print("Creating pickle file for vt...")
with open('vt.dat', 'wb') as fp:
    pickle.dump(vt, fp)
print("Done.")

print("Creating prediction matrix...")
preds = np.around(np.dot(u.T, np.dot(np.diag(s), vt)))
print("Done.")
print(preds.shape)

print ("Writing prediction matrix to file...")
with open('predictions_matrix.dat', 'wb') as fp:
    pickle.dump(preds, fp)
print("Done.")
