# Machine Learning Engineer Nanodegree
## Capstone Proposal
Lars Erik Bolstad
November 16, 2018

## Book Recommendation Engine

### Project overview

The goal of this project is to implement a recommendation engine for books. 

Recommendation engines, or *Recommender systems*, are widely deployed to offer users recommended content or products. Such systems broadly fall into two categories depending on the model and algorithms used: *Collaborative* and *Content-based* filtering [1]. Collaborative filtering models produce recommendations based on a user's past behaviour and preferences, as well as those of other users exhibiting similar preferences. Content-based models are based on characteristics of the product or content in question to recommend items with similar properties. *Hybrid* recommender systems combine these two approaches.

### Problem Statement

Regardless of the model used a recommendation engine needs information about a given user's preferences in order to provide recommendations perceived as relevant and useful. Without such information we have what is known as the *cold-start problem*. 
Our recommendation engine needs to be able to cope with this scenario, as well as the preferred case where it actually can access such data directly. 

The recommendation engine will be based on a Kaggle dataset containing user ratings for 10,000 "popular" books from [Goodreads](https://www.goodreads.com). The dataset is available [here](https://www.kaggle.com/zygmunt/goodbooks-10k/home). In this project I will use an updated version of the dataset with duplicates removed and many more ratings (around 6 million) retrieved from [this source](https://github.com/zygmuntz/goodbooks-10k).

The dataset contains limited data on each book, which means that a content-based filtering approach would need additional data from another source. The dataset does contain around 34,000 user-defined *tags* along with around 1 million combinations of these tags applied to books. However, an initial inspection of this data shows that the overall quality is low and suggests that a useful subset of this data could end up being too small for such a purpose.

In addition to this dataset I will make use of [Goodreads APIs](https://www.goodreads.com/api). Recommendations for users who have a Goodreads account will be based on fetching their reading history using this API. I have personally used Goodreads actively since the service appeared almost 10 years ago and look forward to testing the end result in this project on my own account data!

Goodreads also offers API endpoints for retrieving more detailed data about a book, such as a back-cover synopsis, which could be used to build a content-based model. I will evaluate this approach as part of the project.

One challenge with this dataset worth noting right at the outset is that it only contains a subset of the books in the Goodreads database. Being more than a year old it only contains books published before early 2017, for instance. An initial test based on fetching the list of books read from my own account via the API shows that only 98 of 200 books are present in the dataset. This is a sample of one, but it could mean that the input to the recommendation engine becomes more limited for users whose reading habits don't align well with the majority of readers.

### Solution Statement

As mentioned above, the recommendation engine will need to handle two scenarios: Either we have access to a user's preferences (reading history, perhaps with a rating of each book) via Goodreads' APIs, or we will have to ask the user to indicate in some way what kind of books he or she likes to read.

For the first scenario the recommendations will be based on similar users' preferences (books read along with their ratings) in the dataset. The initial assumption is that a model based on Matrix Factorization should be feasible to build and train based on this dataset. By splitting the data in a training and test set we can use the prediction accuracy as an **evaluation metric** to say something about the performance of the recommendation engine.

For the second scenario where we don't have any information about the user's preferences, the solution will be to first present the user with a number of books and ask for some kind of opinion (a rating, a thumbs-up or thumbs-down, or similar) and use this input to produce recommendations. Here a different model will need to be built, with a rating-based clustering of users and books. An initial strategy for selecting books to present would be to pick the *n* top rated books from each cluster. Based on the user's input we should be able to assign him or her to one of the clusters and recommend books that other users in this cluster rate highly. 

In terms of measuring the peformance of the recommendation engine we will be able to objectively calculate the accuracy of its predictions for the first model described above. In the second scenario, but also to some extent in the first, the most important measure will perhaps be the user's perception of the quality if the recommendations that matter in the end. If I am consistently recommended books that I don't find interesting it is no consolation that the model has a high prediction accuracy. Perhaps those other users aren't so similar after all. 




[1] https://en.wikipedia.org/wiki/Recommender_system

