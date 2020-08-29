#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 21:39:46 2020

@author: pavitravobilisetty
"""

from flask import Flask, request, render_template, session, send_file
from Database import signup, security, helpers
import dash
import dash_html_components as html
import dash_core_components as dcc
from recommender import recommenders
from recommender import recommender2
from recommender import recommender3
from dash.dependencies import Input, Output
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import os
import dash_bootstrap_components as dbc



# Creating a flask instance
server = Flask(__name__)
# Setting a secret key to run simultaneous dash and flask apps
server.secret_key = os.urandom(24)

# Global variables to pass data between flask and dash
user_id = 0
books_id = 0

## Importing the books!

# Setting variables to populate dash dropdowns
genres = {'fiction', 'mystery', 'historical fiction', 'non-fiction', 'young-adult', 'crime', 'comics', 'paranormal', 'thriller', 'biography', 'romance', 'graphic', 'children', 'poetry', 'fantasy', 'history'}
books = helpers.get_books()
users = helpers.get_users()
authors = helpers.get_authors()
main_books = []


# Method that runs after the user clicks sign up
@server.route("/", methods=['GET', 'POST'])
def signups():
    try:
        if request.method == 'POST':
            # get the user input
            check_items = request.form.getlist('genre')
            items = request.form
            # check if the confirm password and the password are the same
            if items['pwd']!= items['cpwd']:
                return render_template("signup.html", error='Passwords should match!')
            # if the username is available, the user is redirected to login page
            if signup.enter_new_user(items['username'],items['pwd'],','.join(check_items)):
                signup.enter_security(items['username'],items['question'], items['answer'])
                return render_template("index.html", message = "Let's Get Started! :D")
            #if the username is already taken, the user has to find a new one!
            else:
                return render_template("signup.html", error='Username Already Exists!')
    except:
        return render_template("signup.html", error='Try Again!')
    return render_template("signup.html")
    

#method called when login is clicked
@server.route("/login", methods=['GET', 'POST'])
def login():
    try:
        user_books = []
        # Sets a global books list to display to the user once he clicks on home on the nav bar 
        global main_books, user_id
        if request.method == 'POST':
            # Get the user inputs
            items = request.form
            session['username'] = items['username']
            print(session['username'])
            #Verify if user entered the correct credentials
            if security.get_user_pass(items['username'],items['pass']) == 1:
                #Get the user details
                table = helpers.get_user_by_name(session['username'])
                user_id = table[0][0]
                helpers.add_collection(user_id)
                #Get recommended books for the user based on interests during sign up
                user_books = recommender2.recommender_2(table[0][3].split(','), books)
                print(table[0][3])
                for i in books:
                    if i[0] in user_books[0:12]:
                        main_books.append(i)
                # User is logged in and can see his main page!
                return render_template("mainpage.html", books = main_books )
            # If user credentials do not match, user is redirected to login
            else:
                return render_template("index.html", message = 'Try Again!')
    except:
        return render_template("index.html", message = 'Try Again!')
    return render_template("index.html", message = 'Welcome Back! :D')

#Method to handle forgot password
@server.route("/forgot", methods=['GET','POST'])
def forgot():
    try:
        if request.method == 'POST':
            # Get the user inputs
            forgot_items = request.form
            sql = security.reset_password(forgot_items['username'])
            # Check if the security question and answer match
            if sql[0][1] == forgot_items['question'] and sql[0][2] == forgot_items['ans']:
                security.new_pass(forgot_items['username'],forgot_items['pwd'])
                return render_template("index.html", message = 'Reset Successful!')
            else:
                return render_template("resetpass.html", error = 'Try Again!')
    except:
        return render_template("resetpass.html", error = "Reset Insuccessful!")
    return render_template("resetpass.html")

#Method to display book details based on the book clicked
@server.route("/book_display/<book_id>",methods=['GET','POST'])
def book_display(book_id):
    global books_id
    if request.method == 'POST':
        # Get the user input
        collections = request.form
        # If the user submits a review
        if 'submitreview' in dict(collections).keys():
            # Review and rating are added into the database
            review=collections['review']
            rating=collections['star']
            helpers.add_review(user_id,books_id,review,rating)
            reviews_list = []
            user_list = []
            rating_list = []
            # Get all the reviews for the particular book from the db
            review_list = helpers.get_reviews(books_id)
            # Add reviews, users, ratings to a list and return to the html page
            for i in range(len(review_list)):
                reviews_list.append(review_list[i][0])
                user_list.append(review_list[i][2])
                rating_list.append(review_list[i][1])
            books_list = helpers.get_book_by_id(books_id)
            books_list = books_list[0]
            table = helpers.get_unique_collection(user_id)
            return render_template("books.html", message = 'Review added!', title = books_list[1], author = books_list[2],isbn = books_list[4],\
                          review = zip(reviews_list,rating_list,user_list), rate = rating, year = int(float(books_list[6])),res1 = books_list[3],res2 = books_list[10],img_url = books_list[7], collections = table)
        
        # If the user clicks on remove a collection   
        if 'remove' in dict(collections).keys():
            name=collections['collection']
            # Helper function called to remove the book
            helpers.remove_book(name, user_id,books_id)
            books_list = helpers.get_book_by_id(books_id)
            books_list = books_list[0]
            table = helpers.get_unique_collection(user_id)
            return render_template("books.html", message = 'Book removed from the selected Collection!', title = books_list[1], author = books_list[2],isbn = books_list[4],\
                          year = int(float(books_list[6])),res1 = books_list[3],res2 = books_list[10],img_url = books_list[7], collections = table)
        # If the user just wants to add to his collection 
        if len(collections)>1:
            name=collections['collection']
            if 'read' in dict(collections).keys():
            # Checks if the book is read or unread
                toggle = 1
            else:
                toggle = 0
          
        helpers.add_book_to_collections(user_id, 1, books_id, toggle,name)
        books_id = book_id
        books_list = helpers.get_book_by_id(book_id)
        books_list = books_list[0]
        table = helpers.get_unique_collection(user_id)
        return render_template("books.html", message = 'Book added to the selected Collection!', title = books_list[1], author = books_list[2],isbn = books_list[4],\
                          year = int(float(books_list[6])),res1 = books_list[3],res2 = books_list[10],img_url = books_list[7], collections = table)
    # Get the book details and the reviews ever written for the book
    if book_id.isdigit():
        books_id = book_id
        books_list = helpers.get_book_by_id(book_id)
        reviews_list = []
        user_list = []
        rating_list = []
        review_list = helpers.get_reviews(books_id)
        
        if len(review_list)>0:
            for i in range(len(review_list)):
                reviews_list.append(review_list[i][0])
                user_list.append(review_list[i][2])
                rating_list.append(review_list[i][1])
            result = zip(reviews_list,rating_list,user_list)
        else:
            reviews_list = ['No user reviews yet! Be the first to review!']
            user_list = ['']
            rating_list = ['*']
            result = zip(reviews_list,rating_list,user_list)
        books_list = books_list[0]
        table = helpers.get_unique_collection(user_id)
        return render_template("books.html", title = books_list[1], author = books_list[2],isbn = books_list[4],\
                          rate = '*', review = result, year = int(float(books_list[6])),res1 = books_list[3],res2 = books_list[10],img_url = books_list[7], collections = table)
    else:
        return send_file("templates/background.jpg",  mimetype='image/gif')
    

# Method to render the account page
@server.route("/account",methods=['GET', 'POST'])
def account():
    # Just display user details if no genres are added
    if request.method == 'GET':
        users = helpers.get_user_by_name(session['username'])
        users = users[0]
        return render_template("account.html",name = users[1], interests = users[3])
    # If new genres are added, add to the db and display user details
    if request.method == 'POST':
        genre_list = request.form.getlist('genre')
        users = helpers.get_user_by_name(session['username'])
        users = users[0]
        helpers.update_interests(users[0],users[3]+','+','.join(genre_list))
        users = helpers.get_user_by_name(session['username'])
        users = users[0]
        return render_template("account.html",name = users[1], interests = users[3])
  
#Method to render the home page when nav bar is clicked
@server.route("/home",methods=['GET', 'POST'])
def home():
    return render_template("mainpage.html", books = main_books )


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://www.w3schools.com/w3css/4/w3.css',dbc.themes.BOOTSTRAP]

app1 = dash.Dash(__name__,external_stylesheets=external_stylesheets,server=server,\
                 url_base_pathname='/explore/')


app1.config['suppress_callback_exceptions']=True


'''app1.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('Column 1'),
            dcc.Graph(id='g1', figure={'data': [{'y': [1, 2, 3]}]})
        ], className="three columns"),

        html.Div([
            html.H3('Column 2'),
            dcc.Graph(id='g2', figure={'data': [{'y': [1, 2, 3]}]})
        ], className="three columns"),
        html.Div([
            html.P('Column 3'),
            html.Img(id='image', src = "https://images.gr-assets.com/books/1346107613m/61672.jpg")
        ], className="three columns"),
        html.Div([
            html.H3('Column 4'),
            dcc.Graph(id='g4', figure={'data': [{'y': [1, 2, 3]}]})
        ], className="three columns"),


    ], className="row")
])
'''
app1.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

app1.scripts.config.serve_locally = False

nav = dbc.Nav([
dbc.NavItem(dbc.NavLink("HOME", href="http://127.0.0.1:8001/home")),
dbc.NavItem(dbc.NavLink("COLLECTIONS", href="http://127.0.0.1:8001/collections/")),
dbc.NavItem(dbc.NavLink("EXPLORE", active=True, href="http://127.0.0.1:8001/explore/")),
dbc.NavItem(dbc.NavLink("ACCOUNT", href="http://127.0.0.1:8001/account")),
],
pills=True,
)
  

app1.layout = html.Div(
    [     
        html.Div(html.P()),
        nav,
        html.Div(id='books-users', children = dcc.Dropdown(
            id='selector-dropdown',
            options=[{'label':i, 'value':i} for i in ['Books', 'Users', 'Recommender']],
            placeholder = "What do you want to search?",
        )),
        html.Div(id='books-users-variable')
    ]
)

## First call back to see if the user wants to search other books or users!
@app1.callback(
    Output('books-users-variable', 'children'),
    [Input('selector-dropdown', 'value')]
)
def booksorusers(selector):

    if selector == 'Books':
        child = [dcc.Dropdown(
            id='genre-dropdown',
            options=[{'label':i, 'value':i} for i in sorted(list(genres))],
            value=[],
            searchable = True,
            multi = True,
            placeholder = "Select a genre!",
        ),
        dcc.Dropdown(
            id='author-dropdown',
            options=[{'label':i, 'value':i} for i in sorted(authors)],
            value=[],
            searchable = True,
            multi = True,
            placeholder = "Select an Author!"
        ),
        dcc.Checklist(
        id = 'checklist-rating',
        options=[
            {'label': 'Greater than 0', 'value': 0},
            {'label': 'Greater than 1', 'value': 1},
            {'label': 'Greater than 2', 'value': 2},
            {'label': 'Greater than 3', 'value': 3},
            {'label': 'Greater than 4', 'value': 4},
            {'label': 'Greater than 5', 'value': 5}
        ],
        value=[0],
        labelStyle={'display': 'inline-block'}
        ),
        html.Div(id='div_variable')]
        return child 
    ## Return Users    
    elif selector == 'Users':
        child = [dcc.Dropdown(
            id='user-dropdown',
            options=[{'label':i[1], 'value':i[0]} for i in users],
            value=1,
            searchable = True,
            placeholder = "Select a User!",
        ),
        html.Div(id='div_variable-1')]
        return child
    elif selector == "Recommender":
        child = [
            dcc.Dropdown(
            id='Recommender-dropdown',
            options=[{'label':i, 'value':i} for i in ['Title Based Recommender', 'Rating Based Recommender', 'Genre Based Recommender']],
            value = '',
            searchable = True,
            placeholder = "Select a recommender engine....",
            ),
            dcc.Dropdown(
            id='recommend-books-dropdown',
            options=[{'label':i[1], 'value':i[0]} for i in books],
            value = -1,
            searchable = True,
            placeholder = "Select a Book and get recommendations...",
            ),
            html.Div(id='div_variable-2')]
        return child


## Second call back for searching the books!
@app1.callback(
    Output('div_variable', 'children'),
    [Input('genre-dropdown', 'value'),
     Input('author-dropdown', 'value'),
     Input('checklist-rating', 'values')]
)
def search_books_for_callback(search_genre, search_author, ratings):
    if ratings == None:
        ratings = [0]
    searched_books = helpers.search_books(search_genre, search_author, ratings)

    return_list = []
    if len(searched_books) >= 100: 
        for i in range(0, 96, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7], style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7], style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7], style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7], style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
            
    ## If the searched books are less than 100!
    elif len(searched_books) < 100:
        if len(searched_books) % 4 == 0:
            for i in range(0, len(searched_books) - 4, 4):
                return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i+1][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image3'+ str(i), src = searched_books[i+2][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                    html.Img(id='image4'+ str(i), src = searched_books[i+3][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
            ], className="row"))
        
        ## If there are books which is not divisible by 4 and if it just 1 off needs another entry at the end!
        elif ((len(searched_books) - 1) % 4) == 0:
            i =0
            try:
                for i in range(0, len(searched_books) - 5, 4):
                    return_list.append(html.Div([
                    html.A([
                        html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                        html.Img(id='image1' + str(i), src = searched_books[i][7], style={'margin-left': '30px',  'width':'174px'})
                    ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

                    html.A([
                        html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                        html.Img(id='image2'+ str(i), src = searched_books[i+1][7], style={'margin-left': '30px',  'width':'174px'})
                    ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
                    html.A([
                        html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                        html.Img(id='image3'+ str(i), src = searched_books[i+2][7], style={'margin-left': '30px',  'width':'174px'})
                    ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
                    html.A([
                        html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                        html.Img(id='image4'+ str(i), src = searched_books[i+3][7], style={'margin-left': '30px',  'width':'174px'})
                    ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
                ], className="row"))
            except IndexError:
                return_list = []

            return_list.append(html.Div([
            html.A([
                html.P(searched_books[-1][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[-1][7], style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[-1][0]), className="three columns"),
            ], className="row"))

            
        ## If there are books which is not divisible by 4 and if it just 2 off needs another 2 entries at the end!
        elif ((len(searched_books) - 2) % 4) == 0:
            i =0
            for i in range(0, len(searched_books) - 6, 4):
                return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i+1][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image3'+ str(i), src = searched_books[i+2][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                    html.Img(id='image4'+ str(i), src = searched_books[i+3][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
            ], className="row"))
            

            return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i-2][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i-1][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
            ], className="row"))
            
        ## If there are books which is not divisible by 4 and if it just 3 off needs another 3 entries at the end!
        elif ((len(searched_books) - 3) % 4) == 0:
            i =0
            for i in range(0, len(searched_books) - 7, 4):
                return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i+1][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image3'+ str(i), src = searched_books[i+2][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                    html.Img(id='image4'+ str(i), src = searched_books[i+3][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
            ], className="row"))
            

            return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i-3][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i-3][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-3][0]), className="three columns"),
                
                html.A([
                    html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i-2][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i-1][7], style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
            ], className="row"))
                


    return return_list


## User collection display !
@app1.callback(
    Output('div_variable-1', 'children'),
    [Input('user-dropdown', 'value')]
)
def get_collections_1(id):
    selected_collections = helpers.get_collections(id)
    name_of_collections = list(set([col[-1] for col in selected_collections]))
    child = [dcc.Dropdown(
            id='collection-dropdown',
            options=[{'label':i, 'value':i} for i in name_of_collections],
            value='',
            searchable = True,
            placeholder = "Select a collection!",
        ),
        html.Div(id='div_variable-collections')]
    return child

    
## Showing the books in each collection!
@app1.callback(
    Output('div_variable-collections', 'children'),
    [Input('user-dropdown', 'value'),
    Input('collection-dropdown', 'value')]
)
def show_collection_books(user_id, selected_collection):
    collections_books = helpers.get_collections(user_id)
    book_ids = []
    for col in collections_books:
        if col[-1] == selected_collection:
            book_ids.append(col[2])

    ## Storing the searched books!
    searched_books = []
    return_list = []
    for buk in books:
        if buk[0] in book_ids:
            searched_books.append(buk)

    ## Displaying the recommended books!
    if len(searched_books) == 0:
        return (html.H1("No Books!"))
    elif len(searched_books) % 4 == 0:
        for i in range(0, len(searched_books) - 4, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
    
    ## If there are books which is not divisible by 4 and if it just 1 off needs another entry at the end!
    elif ((len(searched_books) - 1) % 4) == 0:
        i =0
        try:
            for i in range(0, len(searched_books) - 5, 4):
                return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                    html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
            ], className="row"))
        except IndexError:
            return_list = []

        return_list.append(html.Div([
        html.A([
            html.P(searched_books[-1][1], style = {'text-align' : 'center' }),
            html.Img(id='image1' + str(i), src = searched_books[-1][7],  style={'margin-left': '30px',  'width':'174px'})
        ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[-1][0]), className="three columns"),
        ], className="row"))

        
    ## If there are books which is not divisible by 4 and if it just 2 off needs another 2 entries at the end!
    elif ((len(searched_books) - 2) % 4) == 0:
        i =0
        for i in range(0, len(searched_books) - 6, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
        

        return_list.append(html.Div([
            html.A([
                html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i-2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

            html.A([
                html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i-1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
        ], className="row"))
        
    ## If there are books which is not divisible by 4 and if it just 3 off needs another 3 entries at the end!
    elif ((len(searched_books) - 3) % 4) == 0:
        i =0
        for i in range(0, len(searched_books) - 7, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
        

        return_list.append(html.Div([
            html.A([
                html.P(searched_books[i-3][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i-3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], className="three columns"),
            
            html.A([
                html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i-2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], className="three columns"),

            html.A([
                html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i-1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], className="three columns"),
        ], className="row"))
            


    return return_list
    

@app1.callback(
    Output('div_variable-2', 'children'),
    [Input('Recommender-dropdown', 'value'),
     Input('recommend-books-dropdown', 'value')]
)
def recommender_system(recommender_type, book_id):
    searched_books = []
    return_list = []

    ## Check if a recommendation mode is sselected!
    if recommender_type == '':
        return (html.H1("Select a mode of recommendation!"))

    ## Check if a book is selected!
    if book_id == -1:
        return (html.H1("Select a Book!"))



    ## Title based recommender ! 
    if recommender_type == 'Title Based Recommender':
        list_of_books = recommenders.recommender_1(book_id)
        for buk in books:
            if buk[1] in list_of_books:
                searched_books.append(buk)


    ## Rating based recommender:
    if recommender_type == 'Rating Based Recommender':
        list_of_books = recommender3.recommender_3(book_id)
        if len(list_of_books) >= 41:
            list_of_books = list_of_books[:40]

        for buk in books:
            if buk[0] in list_of_books:
                searched_books.append(buk)

    ## Genre based recommender!
    if recommender_type == 'Genre Based Recommender':
        book_for_recommender = ''
        for buk in books:
            if buk[0] == book_id:
                book_for_recommender = buk
                break
        
        genres_in_book = book_for_recommender[8].split(',')[:-1]
        recommended_book_ids = recommender2.recommender_2(genres_in_book, books)[:41]

        ## Removing the book selected!
        if book_id in recommended_book_ids:
            recommended_book_ids.remove(book_id)

        return_list.append(html.P("Recommending for the gollowing genres: " + str(genres_in_book)))
        for buk in books:
            if buk[0] in recommended_book_ids:
                searched_books.append(buk)

    
    ## Displaying the recommended books!
    if len(searched_books) == 0:
        return (html.H1("No recommendations!"))
    elif len(searched_books) % 4 == 0:
        for i in range(0, len(searched_books) - 4, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
    
    ## If there are books which is not divisible by 4 and if it just 1 off needs another entry at the end!
    elif ((len(searched_books) - 1) % 4) == 0:
        i =0
        try:
            for i in range(0, len(searched_books) - 5, 4):
                return_list.append(html.Div([
                html.A([
                    html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                    html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

                html.A([
                    html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                    html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                    html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
                html.A([
                    html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                    html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
                ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
            ], className="row"))
        except IndexError:
            return_list = []

        return_list.append(html.Div([
        html.A([
            html.P(searched_books[-1][1], style = {'text-align' : 'center' }),
            html.Img(id='image1' + str(i), src = searched_books[-1][7],  style={'margin-left': '30px',  'width':'174px'})
        ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[-1][0]), className="three columns"),
        ], className="row"))

        
    ## If there are books which is not divisible by 4 and if it just 2 off needs another 2 entries at the end!
    elif ((len(searched_books) - 2) % 4) == 0:
        i =0
        for i in range(0, len(searched_books) - 6, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
        

        return_list.append(html.Div([
            html.A([
                html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i-2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

            html.A([
                html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i-1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
        ], className="row"))
        
    ## If there are books which is not divisible by 4 and if it just 3 off needs another 3 entries at the end!
    elif ((len(searched_books) - 3) % 4) == 0:
        i =0
        for i in range(0, len(searched_books) - 7, 4):
            return_list.append(html.Div([
            html.A([
                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

            html.A([
                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
            html.A([
                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
        ], className="row"))
        

        return_list.append(html.Div([
            html.A([
                html.P(searched_books[i-3][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i-3][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-3][0]), className="three columns"),
            
            html.A([
                html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
                html.Img(id='image1' + str(i), src = searched_books[i-2][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

            html.A([
                html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
                html.Img(id='image2'+ str(i), src = searched_books[i-1][7],  style={'margin-left': '30px',  'width':'174px'})
            ], href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
        ], className="row"))
            


    return return_list



app2 = dash.Dash(__name__,external_stylesheets=external_stylesheets,server=server,\
                 url_base_pathname='/collections/')

## Global variable for user!
collections = helpers.get_collections(user_id)
unique_collections = set()
collection_id_list = []
for i in collections:
	unique_collections.add(i[-1])

def refresh_collections(user_id):
	collections = helpers.get_collections(user_id)

	unique_collections = set()
	for i in collections:
		unique_collections.add(i[-1])

	return unique_collections

nav1 = dbc.Nav([
dbc.NavItem(dbc.NavLink("HOME",href="http://127.0.0.1:8001/home")),
dbc.NavItem(dbc.NavLink("COLLECTIONS", active=True, href="http://127.0.0.1:8001/collections/")),
dbc.NavItem(dbc.NavLink("EXPLORE", href="http://127.0.0.1:8001/explore/")),
dbc.NavItem(dbc.NavLink("ACCOUNT", href="http://127.0.0.1:8001/account")),
],
pills=True,
)
  

app2.layout = html.Div(id = 'main-layout',
    children = [
        html.Div(html.P()),
        nav1,
        html.Div(id='collection-dropdown', children = 
        	dcc.Dropdown(
            id='selector-dropdown',
            options=[{'label':i, 'value':i} for i in ['View Collection', 'Add New Collection', 'Delete a Collection!']],
            value = 'NONE',
            placeholder = "What action do you want to perform?",
        )),
        html.Div(id='delete-add-variable')
    ]
)



## ADD a new collection!
@app2.callback(
    Output('delete-add-variable', 'children'),
    [Input('selector-dropdown', 'value')]
)
def trial(inp):
	

	unique_collections = refresh_collections(user_id)
	if inp[0] == 'A':
		return_list = [dcc.Input(id="input1", type="text", placeholder="Enter name", value = "")
				,
				dcc.Dropdown(
	            id='book-dropdown',
	            options=[{'label':i[1], 'value':i[0]} for i in sorted(list(books))],
	            value=[],
	            searchable = True,
	            multi = True,
	            placeholder = "Select a book(s) to add to the collection!",
		        )
				,
				html.Button(children=['ADD THIS'], type='submit', id='add-collection-button', n_clicks = 0)
				,
				html.Div(id='collection-added')
				]
		return return_list
	elif inp[0] == 'D':
		return_list = [dcc.Dropdown(
			            id='delete-collection-dropdown',
			            options=[{'label':i, 'value':i} for i in sorted(list(unique_collections))],
			            placeholder = "Which collection do you want to delete? ",
			        ),
					dcc.Input(id="input2", type="text", placeholder="Confirm Name!", value = ""), 
					html.Button(children=['DELETE THIS'], type='submit', id='delete-collection-button', n_clicks = 0),
					html.Div(id='collection-deleted')
			]
		return return_list

	elif inp[0] == 'V': 
		## Print the collections here!
		return_list = [dcc.Dropdown(
			            id='view-collection-dropdown',
			            options=[{'label':i, 'value':i} for i in sorted(list(unique_collections))],
			            placeholder = "Which collection do you want to view? ",

			        ),
					html.Div(id='collection-view')
			]
		return return_list



## Adding a new collection
@app2.callback(
    Output('collection-added', 'children'),

    [Input('add-collection-button', 'n_clicks'),
     Input('book-dropdown', 'value'),
     Input('input1', 'value')]
)
def adding_new_collection_here(clicks, book_list, name_collection):
	if clicks >= 1 and book_list != [] and name_collection != '':
		print(clicks, book_list, name_collection)

		## Adding all the selected books to the new collection!
		for buk in book_list:
			helpers.add_book_to_collections(user_id, 1,buk, 0, name_collection)

		## Refreshing the collections
		unique_collections = refresh_collections(user_id)
		options = [{'label':i, 'value':i} for i in sorted(list(unique_collections))]

		return html.H2(name_collection+ " is ADDED to the collections!")


## Delete a collection!
@app2.callback(
    Output('collection-deleted', 'children'),

    [Input('delete-collection-dropdown', 'value'),
     Input('delete-collection-button', 'n_clicks'),
     Input('input2', 'value')]
)
def delete_a_collection(collection_name, clicks, collection_name_type):
	if clicks >= 1 and collection_name_type != "" and collection_name_type == collection_name:
		helpers.remove_collection(collection_name, user_id)

		return html.H2(collection_name+ " is Deleted from the collections!")


## Delete a collection!
@app2.callback(
    Output('collection-view', 'children'),

    [Input('view-collection-dropdown', 'value')]
)
def view_a_collection(collection_name):

	if collection_name != None:
		book_ids = []
		return_list = [html.Div(html.P('Progress for this Collection')),dbc.Progress(children=str(helpers.get_read_collections(user_id,collection_name))+"%", value=helpers.get_read_collections(user_id,collection_name), striped=True, animated=True)]
		collections = helpers.get_collections(user_id)

		for i in collections:
			if i[2] not in book_ids and i[-1] == collection_name:
				book_ids.append(i[2])


		searched_books = []
		for buk in books:
		    if buk[0] in book_ids:
		        searched_books.append(buk)


	    ## Displaying the recommended books!
		if len(searched_books) == 0:
		    return (html.H1("No Books!"))
		elif len(searched_books) % 4 == 0:
		    for i in range(0, len(searched_books) - 3, 4):
		        return_list.append(html.Div([
		        html.A([
		            html.P(searched_books[i][1], style = {'text-align' : 'center' }),
		            html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

		        html.A([
		            html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
		            html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
		        html.A([
		            html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
		            html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
		        html.A([
		            html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
		            html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
		    ], className="row"))

		## If there are books which is not divisible by 4 and if it just 1 off needs another entry at the end!
		elif ((len(searched_books) - 1) % 4) == 0:
		    #print('less than 100 and offset 1')
		    i =0
		    try:
		        for i in range(0, len(searched_books) - 3, 4):
		            return_list.append(html.Div([
		            html.A([
		                html.P(searched_books[i][1], style = {'text-align' : 'center' }),
		                html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
		            ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

		            html.A([
		                html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
		                html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
		            ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
		            html.A([
		                html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
		                html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
		            ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
		            html.A([
		                html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
		                html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
		            ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
		        ], className="row"))
		    except IndexError:
		        return_list = []

		    return_list.append(html.Div([
		    html.A([
		        html.P(searched_books[-1][1], style = {'text-align' : 'center' }),
		        html.Img(id='image1' + str(i), src = searched_books[-1][7],  style={'margin-left': '30px',  'width':'174px'})
		    ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[-1][0]), className="three columns"),
		    ], className="row"))

		    
		## If there are books which is not divisible by 4 and if it just 2 off needs another 2 entries at the end!
		elif ((len(searched_books) - 2) % 4) == 0:
		    i =0
		    for i in range(0, len(searched_books) - 3, 4):
		        return_list.append(html.Div([
		        html.A([
		            html.P(searched_books[i][1], style = {'text-align' : 'center' }),
		            html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

		        html.A([
		            html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
		            html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
		        html.A([
		            html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
		            html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
		        html.A([
		            html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
		            html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
		    ], className="row"))
		    

		    return_list.append(html.Div([
		        html.A([
		            html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
		            html.Img(id='image1' + str(i), src = searched_books[i-2][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

		        html.A([
		            html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
		            html.Img(id='image2'+ str(i), src = searched_books[i-1][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
		    ], className="row"))
		    
		## If there are books which is not divisible by 4 and if it just 3 off needs another 3 entries at the end!
		elif ((len(searched_books) - 3) % 4) == 0:
		    #print('less than 100 and offset 3')
		    i =0
		    for i in range(0, len(searched_books) - 3, 4):
		        return_list.append(html.Div([
		        html.A([
		            html.P(searched_books[i][1], style = {'text-align' : 'center' }),
		            html.Img(id='image1' + str(i), src = searched_books[i][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i][0]), className="three columns"),

		        html.A([
		            html.P(searched_books[i+1][1], style = {'text-align' : 'center' }),
		            html.Img(id='image2'+ str(i), src = searched_books[i+1][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+1][0]), className="three columns"),
		        html.A([
		            html.P(searched_books[i+2][1], style = {'text-align' : 'center' }),
		            html.Img(id='image3'+ str(i), src = searched_books[i+2][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+2][0]), className="three columns"),
		        html.A([
		            html.P(searched_books[i+3][1], style = {'text-align' : 'center' }),
		            html.Img(id='image4'+ str(i), src = searched_books[i+3][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i+3][0]), className="three columns"),
		    ], className="row"))
		    

		    return_list.append(html.Div([
		        html.A([
		            html.P(searched_books[i-3][1], style = {'text-align' : 'center' }),
		            html.Img(id='image1' + str(i), src = searched_books[i-3][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-3][0]), className="three columns"),
		        
		        html.A([
		            html.P(searched_books[i-2][1], style = {'text-align' : 'center' }),
		            html.Img(id='image1' + str(i), src = searched_books[i-2][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-2][0]), className="three columns"),

		        html.A([
		            html.P(searched_books[i-1][1], style = {'text-align' : 'center' }),
		            html.Img(id='image2'+ str(i), src = searched_books[i-1][7],  style={'margin-left': '30px',  'width':'174px'})
		        ],href='http://127.0.0.1:8001/book_display/'+str(searched_books[i-1][0]), className="three columns"),
		    ], className="row"))
		        


		return return_list



app = DispatcherMiddleware(server, {
    '/dash1': app1.server,
    '/dash2': app2.server,
})

run_simple('127.0.0.1', 8001, application = app, use_reloader=True, use_debugger=True)


