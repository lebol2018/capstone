# Machine Learning Engineer Nanodegree
## Capstone Proposal
Lars Erik Bolstad
November 16, 2018

## Book Recommendation Engine

### Domain background

The goal of this project is to implement a recommendation engine for books. 

Recommendation engines, or *Recommender systems*, are widely deployed to offer users recommended content or products. Such systems broadly fall into two categories depending on the model and algorithms used: *Collaborative* and *Content-based* filtering [1]. Collaborative filtering models produce recommendations based on a user's past behaviour and preferences, as well as those of other users exhibiting similar preferences. Content-based models are based on characteristics of the product or content in question to recommend items with similar properties. Many *hybrid* recommender systems combine these two approaches in various ways.



### Problem Statement

Regardless of the model used a recommendation engine needs information about a given user's preferences in order to provide recommendations perceived as relevant and useful. Without such information we have what is known as the *cold-start problem*. 
Our recommendation engine needs to be able to cope with this scenario, as well as the preferred case where it actually can access such data directly. 

### Datasets and inputs

The recommendation engine will be based on a Kaggle dataset containing user ratings for 10,000 "popular" books from [Goodreads](https://www.goodreads.com). The dataset is available [here](https://www.kaggle.com/zygmunt/goodbooks-10k/home). In this project I will use an updated version of the dataset with duplicates removed and many more ratings (around 6 million) retrieved from [this source](https://github.com/zygmuntz/goodbooks-10k).

The dataset contains limited data on each book, which means that a content-based filtering approach would need additional data from another source. The dataset does contain around 34,000 user-defined *tags* along with around 1 million combinations of these tags applied to books. An initial inspection of this data shows that the overall quality is low. Many of the user-defined tags have no relation to the books (e.g. the format, which year the book was read, etc). There are also many cases of different spellings of essentially the same tags, meaning substantial cleaning will be required to use this data in a content-based model.

In addition to this dataset I will make use of [Goodreads APIs](https://www.goodreads.com/api). Recommendations for users who have a Goodreads account will be based on fetching their reading history using this API. I have personally used Goodreads actively since the service appeared almost 10 years ago and look forward to testing the end result in this project on my own account data!

Goodreads also offers API endpoints for retrieving more detailed data about a book, such as a back-cover synopsis, which could be used to enhance a content-based model. I will evaluate this approach as part of the project.

One challenge with this dataset worth noting right at the outset is that it contains a subset of the books in the Goodreads database. Being more than a year old it only contains books published before early 2017, for instance. An initial test based on fetching the list of books read from my own account via the API shows that only 98 of 200 books are present in the dataset. This is a sample of one, but it could mean that the input to the recommendation engine becomes more limited for users whose reading habits don't align well with the majority of readers.

### Solution Statement

As mentioned above, the recommendation engine will need to handle two scenarios: Either we have access to a user's preferences (reading history, perhaps with a rating of each book) via Goodreads' APIs, or we will have to ask the user to indicate in some way what kind of books he or she likes to read. In the latter case the solution will be to first present the user with a number of books and ask for some kind of opinion (a rating, a thumbs-up or thumbs-down, or similar) and use this input to produce recommendations.

A collaborative recommendation engine will be implemented based on similar users' preferences (books read along with their ratings) in the dataset. The initial assumption is that a model based on Matrix Factorization should be feasible to build and train based on this dataset. 

A content-based recommendation engine will be implemented based on information about the books themselves. Here the user-defined tags enhanced with additional data extracted via APIs will be the basis for a clustering model.

### Benchmark model

A recommendation engine producing random recommendations will be used for benchmarking the different models described above.

### Evaluation metrics

For evaluating the peformance of recommender systems there are several different metrics that can be used [2]. For this project I will use **Precision@n** and **Recall@n**, where *n* is the number of books that will be recommended to the user. *Precision* and *Recall* are common metrics used in binary classification models [3], where precision is defined as *the number of true positives divided by the number of elements labeled as belonging to the positive class*. Recall is defined as *the number of true positives divided by the number of elements actually belonging to the positive class.*

For a rating-based recommender system we will need to set a threshold rating, e.g. 3.5, and consider ratings above this value as positives (or *recommended*) and ratings below this value as negatives (or *not recommended*). A *relevant* book in this case is a book that has an actual rating above the threshold.

The definitions for **precision@n** and **recall@n** are then as follows [4]:

Precision@n = (# of recommended items @n that are relevant) / (# of recommended items @n)
Recall@n = (# of recommended items @n that are relevant) / (total # of relevant items)

### Project design

The initial activity will consist of an analysis of the Goodreads dataset, including an exploration of the data, necessary data type conversions and an evaluation of missing values if any. Characteristics of the dataset will be visualized and examined with respect to suitability to the candidate machine learning models that may be applied. Cleaning and removal of data will be applied based on this analysis.

Also, an exploration of the Goodreads API will be conducted in order to determine which endpoints need to be called to extract a user's reading history as well as potentially other data that may serve as input to the machine learning models.

I will the evaluate potential models for both collaborative and content-based recommendations. My assumption is that Matrix Factorization and specifically a Singular-value decomposition model would be a good approach for collaborative recommendations. 

For content-based recommendations I will look at clustering algorithms in order to categorize books based on their characteristics. Data already in the dataset will be enhanced by retrieving additional about each book using Goodreads' API.

The plan is to deploy the models as part of a web application that provide book recommendations both to users who have an active Goodreads account, and to those that don't.


[1] https://en.wikipedia.org/wiki/Recommender_system
[2] [http://bickson.blogspot.com/2012/10/the-10-recommender-system-metrics-you.html](http://bickson.blogspot.com/2012/10/the-10-recommender-system-metrics-you.html)
[3] [Precision and Recall](https://en.wikipedia.org/wiki/Precision_and_recall)
[4] [Recall and Precision at k for Recommender Systems](https://medium.com/@m_n_malaeb/recall-and-precision-at-k-for-recommender-systems-618483226c54)


