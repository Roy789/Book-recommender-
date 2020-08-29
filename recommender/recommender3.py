from sklearn.cluster import KMeans
import pandas as pd
import os

path = os.getcwd()+'/recommender/final_book_data.csv'
data = pd.read_csv(path)
data_for_use = data[['work_ratings_count', 'ratings_1', 'ratings_2','ratings_3', 'ratings_4', 'ratings_5']]
kmeans = KMeans(n_jobs = -1, n_clusters = 25, init='k-means++')
kmeans.fit(data_for_use)
pred = kmeans.predict(data_for_use)
data['cluster'] = pred
data['cluster'].value_counts()

def recommender_3(book_id):
    ## Finding the cluster of the book!
    current_book_cluster = int(data[data['best_book_id'] == book_id]['cluster'])
    
    ## Recommending all the books assigned to that cluster 
    recommender_book_ids = list(data[data['cluster'] == current_book_cluster]['best_book_id'])
    
    #Returning the recommended book ids for display!
    return recommender_book_ids