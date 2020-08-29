'''This function gets the score for each book!'''
def get_score(interests, book):
    
    book_genre = [i.strip() for i in book[8].split(',')]
    #print(interests,book_genre)
    score = 0
    for i in interests:
        if i in book_genre:
            score += 1
    return score

'''
This is the main function which takes in a list of interests from the users and then returns the book ids in a sorted manner
based on the users interests (It will rank all the books!)
The function can be called in the following way:
get_best_matching_books(interests=['thriller', 'mystery', 'crime'])
returns -> [40425, 5972040, 295, 7624, 69136, 54492, 353342.....]
'''
        
"""Interests is supposed to be a list of interests in lower case """
def recommender_2(interests, books):
    score_dict = {}
    for i in range(len(books)):
        score_dict[i] = get_score(interests, books[i])

    score_dict = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    ranked_book_ids = []

    ranked_book_ids = [books[i[0]][0] for i in score_dict]
    
    return ranked_book_ids