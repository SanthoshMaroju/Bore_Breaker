from flask import Flask,render_template,request
import urllib.request
import pandas as pd
import numpy as np
import json
import ssl
app = Flask(__name__)

api_key="&apikey=8e8ab366"
base_url="http://www.omdbapi.com/?i="
# http://www.omdbapi.com/?i=tt3896198&apikey=8e8ab366

global now_user
now_user="unknown"

@app.route('/future')
def future():
    return render_template('future.html')

@app.route('/signip',methods=['POST','GET'])
def signip_page():
    if request.method=="POST":
        user_name=request.form['user_name']
        passw=request.form['pass']
        repassw=request.form['repass']
        if passw!=repassw:
            return "passwords doesn't match"
        new_df=pd.DataFrame({'user_name':[str(user_name)],'password':[str(passw)],'Action':[int(0)],'Fantasy':[int(0)],'Adventure':[int(0)],'Science Fiction':[int(0)],'Family':[int(0)],'Thriller':[int(0)],'Drama':[int(0)],'Comedy':[int(0)],'Horror':[int(0)],'Romance':[int(0)],'Crime':[int(0)]})

        new_df.to_csv('user_login.csv', mode='a',index=False,header=False)
        global now_user
        now_user=user_name
        return render_template('index.html',value=now_user)
    else:
        return render_template("signip.html")

@app.route('/',methods=["POST","GET"])
def home_page():
    if request.method=="POST":
        user_name=str(request.form['user_name'])
        passw=str(request.form['pass'])
        df=pd.read_csv('user_login.csv')
        if user_name!="":
            new_df=df.loc[df['user_name'].str.contains(user_name)]
            if new_df.empty:
                return render_template("login.html",val="no user")
            else:
                pw=new_df.loc[new_df["password"]==passw]
                if pw.empty:
                    return render_template("login.html",val="wrong")
                else:
                    global now_user
                    now_user=user_name
                    return render_template("index.html",value=now_user)
            # if [df[df['user_name']==user_name]['password']==passw][0][0]:
            #     return render_template("index.html")
            # else:
            #     return "password incorrect"
        else:
            return "invalid username"
    else:
        return render_template("login.html",val="ok")
    # return render_template("index.html")

@app.route('/movies',methods=["POST","GET"])
def movies():
    if request.method == "GET":
        flis=[]
        file=open('file.txt','r')
        flis=file.read().split("\n")
        actor=open('actor.txt','r')
        alis=actor.read().split("\n")
        user_df=pd.read_csv('user_login.csv')
        maxi=-1
        lo=2
        for i,j in zip(user_df[user_df['user_name']==now_user].values[0],user_df[user_df['user_name']==now_user]):
            if lo==0:
                if maxi<int(i):
                    maxgenre=j
                    maxi=int(i)
            else:
                lo=lo-1
        dp=pd.read_csv('tmdb-movies.csv')
        new_dp=dp[dp['genres']==maxgenre]
        new_dp=new_dp.sort_values(["vote_average"],ascending=False)
        lis=[]
        new_dp=new_dp.head(5)
        for i in range(new_dp.shape[0]):
            id=str(new_dp['imdb_id'].values[i])
            ssl._create_default_https_context=ssl._create_unverified_context
            conn=urllib.request.urlopen("http://www.omdbapi.com/?i="+id+"&apikey=8c5398b1")
            json_data=json.loads(conn.read())
            lis.append(json_data)
        return render_template("movies.html",var=flis,value=now_user,actor=alis,rec=lis)
    if request.method=="POST":
        title=request.form['title']
        actor=request.form['actor']
        genre=request.form['genre']
        dp=pd.read_csv('tmdb-movies.csv')
        lis=[]
        if(title!=""):
            ssl._create_default_https_context=ssl._create_unverified_context
            dp=dp[dp['original_title']==title]
            imdb=dp["imdb_id"].values[0]
            conn=urllib.request.urlopen("http://www.omdbapi.com/?i="+imdb+"&plot=full&apikey=8e8ab366")
            json_data=json.loads(conn.read())
            return render_template("output.html",data=json_data,value=now_user)
        else:
            genre=str(genre)
            actor_df=pd.DataFrame()
            actor=str(actor)
            if(actor!=""):
                for i in range(dp.shape[0]):
                    now=str(dp['cast'].values[i]).split('|')
                    for j in now:
                        if j == actor:
                            actor_df=actor_df.append(dp.iloc[i])
                            break;
                dp=actor_df
            genre_df=pd.DataFrame()
            if(genre!=""):
                for i in range(dp.shape[0]):
                    now=str(dp['genres'].values[i]).split('|')
                    for j in now:
                        if j == genre:
                            genre_df=genre_df.append(dp.iloc[i])
                            break;
                user_if=pd.read_csv('user_login.csv')
                user_if.loc[user_if.user_name==now_user,genre]=user_if.loc[user_if.user_name==now_user,genre]+1
                user_if.to_csv('user_login.csv',index=False)
                dp=genre_df
                # return genre_df.head(30).to_html(header="true", table_id="table")
            if dp.empty:
                return render_template("alert.html")
            dp=dp.sort_values(["vote_average"],ascending=False)
            for i in range(dp.shape[0]):
                id=str(dp['imdb_id'].values[i])
                ssl._create_default_https_context=ssl._create_unverified_context
                conn=urllib.request.urlopen("http://www.omdbapi.com/?i="+id+"&plot=full&apikey=8c5398b1")
                json_data=json.loads(conn.read())
                lis.append(json_data)
            return render_template("multi_output.html",datas=lis,value=now_user)

if __name__ == '__main__':  
    app.debug = True
    app.run() 
