import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET
import pickle

user_books = []
n_sim_users = 5
n_recs = 100
r_threshold = 4.0

# Parse the XML response from Goodreads and extract the book IDs and ratings
def parse(response):
    '''
    Input: response - The raw XML response returned by the Goodreads application

    Output: n - The number of books Retrieved
    (book id, rating) stored in the global variable user_books
    '''
    n = 0
    e = ET.fromstring(response)
    for review in e.iter('review'):
        rating = int(review.find('rating').text)
        n += 1
        for bk in review.iter('book'):
            id = bk.find('id').text
            user_books.append((id, rating))

    return n

# Fetch book "reviews" from goodreads
def get_books(id, n, page):
    '''
    Input: id - A Goodreads user id
           n - Number of books to request
           page - The "page" number that we're iterating over until no more books are returned

    Output: rcv - The number of books received
    '''
    req = "https://www.goodreads.com/review/list.xml?key=" + key + "&id=" + id + "&v=2&per_page=" + str(n)
    req += "&page=" + str(page)
    req += "&shelf=read"
    b = requests.get(req)
    rcv = parse(b.content)
    print("Got " + str(rcv) + " books.")
    return rcv

# Convenience function for printing book details
def print_book(id):
    dataset_book = books[books.book_id == id]
    title = str(dataset_book.title.values[0])
    authors = str(dataset_book.authors.values[0])

    print(authors + " : " + title)


print("Read books from file...")
books = pd.read_csv('books.csv')
print("Done.")

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

key = "" # Removed
secret = "" # Removed
user_id = "4343147" # Lars Erik
#user_id = "11796704" # Anne Line

per_page = 200
page = 1

print("Fetching the first batch of books from Goodreads...")
received_books = get_books(user_id, per_page, page)

while (received_books == per_page):
    page += 1
    print("Fetching the next batch of books from Goodreads...")
    received_books = get_books(user_id, per_page, page)


print("Retrieved " + str(len(user_books)) + " books in total.")

n_columns = len(books.book_id.unique())
d = [0] * n_columns;
d = np.array(d)


ratings0 = 0
ratings1 = 0
sumratings = 0

for id, rating in user_books:
    sumratings += rating
    if rating == 0:
        ratings0 += 1
    else:
        ratings1 += 1

uavg = round(sumratings/ratings1,2)
print(str(ratings1) + " of the books have a rating.")
print("Average rating: " + str(uavg))

found_books = []
books_found = 0

for id, rating in user_books:
    dataset_book = books[books.goodreads_book_id == int(id)]
    book_found = (dataset_book.shape[0] == 1)

    if book_found:
        dataset_title = str(dataset_book.title.values[0])
        dataset_book_id = int(dataset_book.book_id.values[0])
#        print(id + " " + dataset_title)
        found_books.append(dataset_book_id)
        books_found += 1
        r = rating

        # Replace non-ratings with the user's average rating!
        if r == 0:
            r = uavg
        d[dataset_book_id - 1] = r

#print(str(len(found_books)) + " of these are in our dataset!")
print(str(np.count_nonzero(d)) + " of the books are in our dataset!")

# Find similar users
print ("Find the " + str(n_sim_users) + " most similar users in the ratings matrix...")
sim = []
for i in list(ratings_matrix.index):
    u2 = ratings_matrix.iloc[i-1].values
    sim.append((i, np.dot(d, u2)))

# sort by similarity
sim = sorted(sim, key=lambda tup: tup[1], reverse=True)

# create list of just the ids
most_similar_users = list(list(zip(*sim))[0])
top10 = most_similar_users[:n_sim_users]

print("Most similar users: " + str(top10))

'''
for u in top10:
    print("Books read by user " + str(u))
    ur = ratings_matrix.iloc[u-1].values
    ub = np.nonzero(ur > r_threshold)[0] + 1
    for bid in ub:
        print_book(bid)


exit(0)
'''
recs = []
# Extract all book ids rated above t by these users from predictions
for u in top10:
    ur = preds.iloc[u-1].values
    msk = ur > r_threshold
    r = list(ur[msk])
    ids = list(np.nonzero(ur > r_threshold)[0] + 1)
    for i in range(len(r)):
        recs.append((ids[i], r[i]))

# Sort recommendations by rating
sorted_recs = sorted(recs, key=lambda tup: tup[1], reverse=True)

# Extract only the book ids
recs = [x[0] for x in sorted_recs]

# Remove duplicates
recs = list(set(recs))

# Remove those already read
recs = list(set(recs) - set(found_books))
print(str(len(recs)) + " recommendations.")

# Set a threshold to avoid always getting the most read books recommended!
rc_threshold = 3000000

# Throw away recommendations of books with more than rc_threshold ratings!
print("Remove those with rating count above " + str(rc_threshold))
high_ratings = list(books[books.ratings_count > rc_threshold].book_id.values)
recs = list(set(recs) - set(high_ratings))
print(str(len(recs)) + " remaining!")


print("RECOMMENDATIONS")
print("---------------")

for bid in recs[:n_recs]:
    dataset_book = books[books.book_id == bid]
    title = str(dataset_book.title.values[0])
    authors = str(dataset_book.authors.values[0])

    print(authors + " : " + title)

print(recs[:n_recs])
