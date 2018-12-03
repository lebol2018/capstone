import functools
import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET
import pickle
import logging
import os
import random


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, session
)

# Read the necessary files

# 1. books.csv
path = os.path.join(os.path.dirname(__file__),'books.csv')
books = pd.read_csv(path)

# 2. user_ratings_matrix.dat as generated by create_utility_matrix.py
# We use this for finding similar users
path = os.path.join(os.path.dirname(__file__),'user_ratings_matrix.dat')
with open(path, 'rb') as fp:
    ratings_matrix = pickle.load(fp)
ratings_matrix = pd.DataFrame(ratings_matrix)

# 3. predictions_matrix.dat, as generated by svd.py
path = os.path.join(os.path.dirname(__file__),'predictions_matrix.dat')
with open(path, 'rb') as fp:
    preds = pickle.load(fp)
preds = pd.DataFrame(preds)


# Parse the raw Goodreads XML response
def parse(response):
    '''
    Input: response - The XML response received from Goodreads
    Output: n - The number of books received
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

# Fetch book "reviews" from the user's Goodreads 'read' shelf
def get_books(id, n, page):
    '''
    Input: id - A Goodreads user id
           n - Number of books to request
           page - The "page number" that we're iterating over until no more books are returned

    Output: rcv - The number of books returned
    '''

    req = "https://www.goodreads.com/review/list.xml?key=" + key + "&id=" + id + "&v=2&per_page=" + str(n)
    req += "&page=" + str(page)
    req += "&shelf=read"
    b = requests.get(req)
    rcv = parse(b.content)
    return rcv

# Pick random books for the user to select
def pick_random_books(already_picked, n):
    '''
    Input: already_picked - The list of book ids already picked
           n - The number of random books requested

    Output: picks - A list of random book ids
    '''
    picks = []
    while len(picks) < n:
        id = random.randint(1,1000) # Pick among the 1000 most read books
        if id not in already_picked:
            picks.append(id)

    return picks

# Find recommendations
def find_recs(top10, found_books, filter):
    '''
    Input: top10 - A list of the most similar users (not necessarily exactly 10)
           found_books - A list of books already read by the user OR selected by the user in the
                         case he/she doesn't have a Goodreads account
           filter - A threshold value used to filter out books with a high ratings count!

    Output: recs - A list containing the book ids of the recommended books
    '''
    recs = []
    # Extract all book ids rated above threshold by these users from predictions
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

    # Throw away recommendations of books with more than 'filter'' ratings!
    high_ratings = list(books[books.ratings_count > filter].book_id.values)
    recs = list(set(recs) - set(high_ratings))

    return recs

# Convenience function that generates a dictionary of book information given a book id
def bookinfo(book_id):
    db = books[books.book_id == book_id]
    b = {}
    b['id'] = book_id
    b['gr_id'] = db.goodreads_book_id.values[0]
    b['author'] = db.authors.values[0]
    b['title'] = db.title.values[0]
    b['img_url'] = db.image_url.values[0]
    return b

# Global variables

userid = "foo"
state = 0
user_books = []
n_sim_users = 5 # The number of similar users to be picked
n_recs = 100 # The number of recommended books to return
r_threshold = 4.0 # Ratings threshold
uavg = 0
per_page = 200
n_random_books = 10 # THe number of random books to be displayed at a time


key = "" # Removed
secret = "" # Removed

bp = Blueprint('rec', __name__, url_prefix='/rec')

# The "main" method
@bp.route('/', methods=('GET', 'POST'))
def gr():
    return render_template('main.html', state=state)

# Fetch books from Goodreads
@bp.route('/fetchbooks', methods=('GET', 'POST'))
def fetch():
    if request.method == 'POST':
        userid = request.form['userid']
        page = 1
        received_books = get_books(userid, per_page, page)

        while (received_books == per_page):
            page += 1
            received_books = get_books(userid, per_page, page)

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

        found_books = []
        books_found = 0

        for id, rating in user_books:
            dataset_book = books[books.goodreads_book_id == int(id)]
            book_found = (dataset_book.shape[0] == 1)

            if book_found:
                dataset_book_id = int(dataset_book.book_id.values[0])
                found_books.append(dataset_book_id)
                books_found += 1
                r = rating

                # Replace non-ratings with the user's average rating!
                if r == 0:
                    r = uavg
                d[dataset_book_id - 1] = r

        session['d'] = d.tolist()
        session['found_books'] = found_books

        s = "Retrieved " + str(len(user_books)) + " books in total. "
        s += str(ratings1) + " of the books have a rating. "
        s += "Average rating: " + str(uavg) + ". "
        s+= str(np.count_nonzero(d)) + " of the books are in our dataset!"
        return s

# Find similar users once books are retrieved from Goodreads, or the users has selected
# the required number of books.
@bp.route('/findsimilarusers', methods=('GET', 'POST'))
def findusers():
    d = np.array(session['d'])
    sim = []
    for i in list(ratings_matrix.index):
        u2 = ratings_matrix.iloc[i-1].values
        sim.append((i, np.dot(d, u2)))

    # sort by similarity
    sim = sorted(sim, key=lambda tup: tup[1], reverse=True)

    # create list of just the ids
    most_similar_users = list(list(zip(*sim))[0])
    top10 = most_similar_users[:n_sim_users]
    session['simusers'] = top10

    return str(top10)

# Pick recommendations
@bp.route('/getrecs', methods=('GET', 'POST'))
def recs():
    filter = int(request.form['filter'])

    top10 = session['simusers']
    found_books = session['found_books']
    recs = find_recs(top10, found_books, filter)[:n_recs]

    bdata = []
    for bid in recs:
        bdata.append(bookinfo(bid))

    return str(bdata)

# Get random books
@bp.route('/getrandombooks', methods=('GET', 'POST'))
def randombooks():
    already_picked = []
    if session.get('already_picked'):
        already_picked = session['alreadypicked']

    picks = pick_random_books(already_picked, n_random_books)
    already_picked.extend(picks)
    session['alreadypicked'] = already_picked

    bdata = []
    for bid in picks:
        bdata.append(bookinfo(bid))

    return str(bdata)

# Method called once the user has finished selecting books
@bp.route('/finishedselection', methods=('GET', 'POST'))
def finished():
    found_books = []

    nb = request.form.get("selectedBooks")
    if nb is not None:
        new_books = request.form['selectedBooks']
        found_books = new_books.split(',')
    session['found_books'] = found_books

    n_columns = len(books.book_id.unique())
    d = [0] * n_columns;
    d = np.array(d)

    for id in found_books:
        dataset_book = books[books.goodreads_book_id == int(id)]
        dataset_book_id = int(dataset_book.book_id.values[0])
        d[dataset_book_id - 1] = 1

    session['d'] = d.tolist()

    s = "You have selected " + str(len(found_books)) + " books. "
    return s