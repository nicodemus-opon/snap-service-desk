from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps
import smtplib
from email import *
import tweepy
from textblob import TextBlob
import numpy as np
import pandas as pd
from datetime import *
import jira.client
from jira.client import JIRA


while True:
    try:
        consumer_key = "w1OfpL5GIeSEzQWAQbVRIrFvU"
        consumer_secret = "iVrMsBaaIlCudtKiIhPBVu3onllfPuleGNoRxwJGHCj0agjtbT"
        access_token = "1004781338841493505-vxy3uLUWSO3sL3Up4HllTg9djN4NdM"
        access_token_secret = "SFaW44avqYqcZRGnIStuQmS8m4QL0F9wXrNmstytpBrDO"

        ## set up an instance of Tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        # login in to mail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("cbsoftlabke@gmail.com", "blacksaint")
        #initialize the mentions as an empty array
        
        print("initialization issa success")
        break
    except Exception as e:
        print("initialization issa failure")
        print(e)

app = Flask(__name__)
app.secret_key = "nico"
app.debug = True


def jira_login(servo="", user_name_="", password=""):
    try:
        options = {'server': servo}
        jira = JIRA(options, basic_auth=(user_name_, password))
        if jira:
            return (True)
        else:
            print("legit false....")
            return (False)
    except Exception as e:
        print("exceptioning....")
        print(e)
        return (False)


def send_mail(toaddr="", body="", fromaddr="Snap Service Desk"):
    # msg = str("From:",fromaddr,"To",toaddr,"Subject","SUBJECT OF THE MAIL", boddy)
    msg = str(body)
    text = msg
    server.sendmail(fromaddr, toaddr, text)
    #server.quit()
    print("completed sending mail")


def search(max_tweets=100, query="", from_mail=""):
    global array_of_ids
    global array_of_comments
    global array_of_time
    global array_of_date
    global array_of_polarity
    global array_of_colors
    global mentions
    global average_sentiment
    global array_of_names

    array_of_stuff = []
    array_of_subs = []
    array_of_avgs = []
    array_of_dates = []
    array_of_names = []

    array_of_ids = []
    array_of_comments = []
    array_of_time = []
    array_of_date = []
    array_of_polarity = []
    array_of_colors = []

    max_tweets=int(max_tweets)
    searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
    try:
        for z in searched_tweets:
            try:
                time_created = z.created_at
                time_created_2 = str(time_created.date().strftime("%a-%d-%m-%y"))
                # print(time_created_2)
                # print(z.text)
                wiki = TextBlob(z.text)
                # print(wiki.sentiment.polarity)
                if wiki.sentiment.polarity != 0.0:
                    if wiki.sentiment.polarity > 0:
                        pass
                    else:
                        user_name = str(wiki[wiki.find("@"):wiki[wiki.find("@")::].find(" ")])
                        print(user_name)
                        array_of_names.append(str(user_name))
                        array_of_stuff.append(str(wiki))
                        print(wiki)
                        tr_day = '"' + str(time_created_2) + '"'
                        array_of_dates.append(time_created_2)
                        array_of_comments.append(z.text)
                        array_of_time.append(str(time_created.time()))
                        array_of_date.append(str(time_created.date()))
                        pp = ""
                        array_of_polarity.append(
                            str(float("{0:.2f}".format((1 + wiki.sentiment.polarity) * 50))) + " % negative")
                        array_of_colors.append("table-danger")
                        ####send_mail(toaddr=user_name, body=wiki)
                        # array_of_subs.append(wiki.sentiment.subjectivity)
                        # avgs=float((wiki.sentiment.polarity + wiki.sentiment.subjectivity)/2)
                        # array_of_avgs.append(avgs)

            except Exception as g:
                # print(g)
                pass
        return ([array_of_stuff, array_of_names])
    except Exception as e:
        pass
        # print(e)

    x = 0.0
    # print(len(array_of_names))
    # print(len(array_of_stuff))
    try:
        for zy in array_of_stuff:
            zy += x
            x = zy
        zy = zy / len(array_of_stuff)
        # print("average=",str(zy),"%")
        perc = zy + 1
        cvf = perc / 2
        cvf = cvf * 100
        average_sentiment = (str(cvf), "%")
        mentions = int(len(array_of_stuff))
        ##
        y_plot = list(reversed(array_of_dates))
        x_plot = str(list(reversed(array_of_stuff)))
        array_of_ids = [de for de in range(len(x_plot))]
        # return (y_plot, x_plot)
    except Exception as d:
        # print(d)
        pass
        ##plt.plot([list(reversed(array_of_dates))[0],list(reversed(array_of_dates))[-1]],[list(reversed(array_of_stuff))[0],list(reversed(array_of_stuff))[-1]],color="green")
        ##plt.plot(range(len(array_of_subs)),array_of_subs,color="red")
        ##plt.plot(range(len(array_of_avgs)),array_of_avgs,color="green")
        ##plt.show()


# search()

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


@app.route('/', methods=['GET', 'POST'])
@is_logged_in
def index():
    if request.method == 'POST':
        mail_x = request.form['service_email']
        tag_to_search = request.form['search_term']
        volume_of_search = request.form['search_volume']
        print("##########")
        print(mail_x)
        print(tag_to_search)
        print(volume_of_search)
        print("##########")
        
        list_of_tweets=search(max_tweets=volume_of_search, query=tag_to_search, from_mail=mail_x)
        session["mentions"] = list(list_of_tweets[0])
        session["names"] = list(list_of_tweets[1])
        session["mentions_len"] =len(session["mentions"])
        ###########this is where you left off
        ###'in <string>' requires string as left operand, not int
        ###list index out of range
        for cvf in range(len(session["mentions"])):
            try:
                send_mail(toaddr=str(mail_x).encode("utf-8"), body=str(session["mentions"][cvf]).encode("utf-8"), fromaddr=str(["names"][cvf]).encode("utf-8"))
            except Exception as e:
                print("email error")
                print(e)
        return (render_template('index.html'))
    else:
        session["mentions"] = []
        session["mentions_len"] =len(session["mentions"])
        return (render_template('index.html'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        servo = request.form['server']
        session['_servo_'] = servo
        session['_user_name_'] = username
        session['_password_'] = password
        print(str(session['_servo_']))
        print(str(session['_user_name_']))
        print(str(session['_password_']))
        log_in = jira_login(servo=session['_servo_'], user_name_=session['_user_name_'], password=session['_password_'])
        print(str(log_in))

        print("got post req")
        if log_in == True:
            session['logged_in'] = True
            print("yebooo")
            return redirect('/')
        elif log_in == False:
            # session['logged_in']=False
            print("login failed")
            return render_template('login.html')
    else:
        # log_in=jira_login(servo=session['_servo_'],user_name_=session['_user_name_'],password=session['_password_'])
        ##        if log_in == 1:
        ##            session['logged_in'] = True
        ##            return render_template('index.html')
        ##        elif log_in == 0:
        # session['logged_in']=False
        return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8090)
