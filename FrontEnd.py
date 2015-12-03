import bottle
import httplib2
__author__ = 'Shane'
# -*- coding: utf-8 -*-
from bottle import *
import math
from operator import itemgetter
from collections import Counter
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
#from googleapiclient.client import *
from beaker.middleware import SessionMiddleware
import sqlite3 as sql
import os

runLocal =0 #if 1 run on localhost if 0 run on aws
baseURL= ""
if runLocal==1:
    baseURL = "http://localhost:8080"
else:
    baseURL = "http://ec2-52-22-145-42.compute-1.amazonaws.com"

redirect_uri_ = baseURL + "/redirect"
redirect_search_uri = baseURL+ '/search'
redirect_login_done = baseURL + '/login/done'

Fout = open ('History.txt',"w")
Fout.write("")
Fout.close()
session_opts = {
	'session.type': 'file',
	'session.cookie_expires': 300,
	'session.data_dir': './data',
	'session.auto': True,
}
app = SessionMiddleware(app(), session_opts)

class user ():
    name=""


#con = sql.connect('FrontEnd.db')
#cur = con.cursor()
#cur.execute("CREATE TABLE History(Email TEXT, Word TEXT, Occurance INT)")

userID = 0
userID_dict ={}
is_logged_in_dict = {}

is_logged_in = False
CLIENT_ID = '551536065271-6amm44978svikopsnh9165tl07gakikt.apps.googleusercontent.com'
CLIENT_SECRET = '264Yp1iGSWW0IUB4sqvFdGh4'
scope = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
#scope = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/plus.profile.emails.read'

user_email = ""
user_name_first =""
user_name_last =""
wordFrequency =[]
histogram=[]

#########################################################################
###################       BUTTONS AND SHIT       ########################
#########################################################################
login_button_uri = baseURL + "/login"
logout_button_uri = baseURL + "/logout"

login_button = """
<FORM METHOD="LINK" ACTION="/login" ALIGN = "left">
<INPUT TYPE="submit" VALUE="Login">
</FORM>
"""

title_logo = """
<h1>3PP</h1>
"""

logout_button = """
<FORM METHOD="LINK" ACTION="/logout" ALIGN = "left">
<INPUT TYPE="submit" VALUE="Logout">
</FORM>
"""

search_button = """
            <form action ="/search" method="post">
            <input name="keywords" type = "text" />
            <input value = "Search" type="submit" />
            </form>
"""

#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
@route ('/test', method='GET')
def test():
    pass


@route ('/', method='GET')
def home():
    redirect(redirect_search_uri)

@route('/login')
def login_page():

    flow = flow_from_clientsecrets("client_secrets.json", scope, redirect_uri=redirect_login_done)
    #flow = flow_from_clientsecrets("client_secrets.json", scope, redirect_uri=redirect_search_uri)
    uri = flow.step1_get_authorize_url()
    global is_logged_in
    print "@login:redirecting to google"
    redirect(uri)
    #bottle.redirect(str(uri))
    return

@route('/login/done')
def login_done_redirect():
    global redirect_search_uri
    global user_email
    global userID
    global is_logged_in
    global is_logged_in_dict
    #Google Auth Stuff here
    test =0
    if test ==0:
        code=request.query.get('code','')
        #flow = OAuth2WebServerFlow(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,scope=scope,redirect_uri=redirect_search_uri)
        flow = OAuth2WebServerFlow(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,scope=scope,redirect_uri=redirect_login_done)
        credentials = flow.step2_exchange(code)
        token = credentials.id_token['sub']
        test=1
    http = httplib2.Http()
    http = credentials.authorize(http)

    #get user email
    users_service = build('oauth2','v2',http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']

    print "@login/done:user is now logged in, redirect to search page"
    #redirect(redirect_search_uri)
    is_logged_in = True

    redirect(redirect_search_uri)

@route('/logout')
def logout_page():
    global is_logged_in
    global user_email
    global wordFrequency
    global histogram

    is_logged_in=False
    print "@logout:user is being logged out, redirect to google logout page"
    user_email=""

    wordFrequency = []
    histogram=[]
    redirect("https://accounts.google.com/logout")
    #redirect('http://localhost:8080')
    #save session shit here so we can remember what the user searched.
    return

@route('/search', method ='GET')
def search_page_get():
    print "im in search"

    global is_logged_in
    global user_email
    loginStateList = []
    loginStateList.append(is_logged_in)
    loginStateList.append(user_email)
    if is_logged_in==True:

#        argsList.append("True")
#        argsList.append(user_email)
        return bottle.template ('Templates/search', loginStateList = loginStateList)
    else:
#        argsList.append(is_logged_in)
        return bottle.template ('Templates/search', loginStateList = loginStateList)



@route('/search', method='POST')
def search_page_post():
    search = request.forms.get('keywords')
    print"/search"
    print search
    search = search.split()
    print search
    #grab the keyword from the text input form and redirect to the first page of the keyword
    print "/search end"
    redirectURLTemp = baseURL+ "/search/" + search[0]
    for x in range(len(search)-1):
        redirectURLTemp += "+" + search[x+1]

    redirectURLTemp +="/1"
    redirect ( redirectURLTemp )

@route('/search/<searchTerm>/<pageNumber>', method='GET')
def search_page_results(searchTerm,pageNumber):
    global is_logged_in
    global user_email
    print type(searchTerm)
    ctrlList = []
    urlList = []
    loginStateList = []
    searchTerm = searchTerm.split("+")
    #query database for search terms and pass them to the search results template
    #find number of pages, count # of items in list returned by query, divide by 5, ceil the number for total number of pages
    #add number of pages to argsList
    #add current page number to argsList
    #argslist format (is_logged_in , email address , number of pages)
    #need to store list of URLs for the page.
    #resultsList format (URL1, URL2,URL3,URL4,URL5)

    conn = sql.connect('backend.db')
    c = conn.cursor()
    searchTermWord=""
    #if len(searchTerm) ==1:
    #    searchTermWord =  searchTerm
    #else:
    searchTermWord = searchTerm[0]
    print "I am searching for:%s"%searchTermWord
    query="""
    SELECT Document.doc_url,PageRank.rank
    FROM Document,PageRank,Lexicon,InvertIndex
    WHERE Lexicon.words = "%s"
	    AND InvertIndex.WordId=Lexicon.Id
	    AND Document.Id =InvertIndex.DocId
	    AND Document.Id=PageRank.DocId
    ORDER BY PageRank.rank DESC
    """ %searchTermWord.lower()

    #c.execute(SELECT Document.doc_url,PageRank.rank FROM Document INNER JOIN ON Document.Id=PageRank.DocId )
    #c.execute("SELECT Document.doc_url,PageRank.rank FROM Document,PageRank WHERE Document.Id=PageRank.DocId ORDER BY PageRank.rank DESC")
    c.execute(query)

    urlData = c.fetchall() #urlData contains the queried URL data from the database
    print "urldata start"
    print urlData
    print "end urldata"


    if len(urlData)<5:
        urlList=urlData
    #else:
    #    for x in range(int(pageNumber)*5-5,(int(pageNumber)*5)):
    #        urlList.append(urlData[x])
    else:
        remainder = len(urlData)%5
        for i in range(len(urlData)):
            if i>=((int(pageNumber)*5)-5) and i<=int(pageNumber)*5:
                urlList.append(urlData[i])



    currentPageNumber = pageNumber
    totalNumberPage = math.ceil(float(len(urlData))/5)
    loginStateList.append(is_logged_in)
    loginStateList.append(user_email)

    ctrlList.append(searchTermWord)
    ctrlList.append(int(totalNumberPage))
    ctrlList.append(currentPageNumber)


    print loginStateList
    print ctrlList
    print urlList
    return bottle.template ('Templates/search_results', loginStateList = loginStateList,ctrlList = ctrlList, urlList = urlList)
    #return bottle.template ('Templates/search_results', loginState = loginStateList, ctrlData = ctrlList, urlData = urlList)



#This displays the error page when an invalid URL is typed into the browser
@error(404)
def error404(error):
    return 'You seem to be lost... '

#This runs the webserer on host 'localhost' and port 8080. Can be accessed using http://localhost:8080/
if runLocal==1:
    run(host='localhost', port=8080, app=app)
else:
    run(host='0.0.0.0', port=80, app=app)

