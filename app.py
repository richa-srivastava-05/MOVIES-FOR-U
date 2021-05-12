from flask import Flask , render_template,session,request
import MySQLdb
import json

dbConn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='richa',db='data') or die ("couldn't connect")
mycursor=dbConn .cursor()
app = Flask(__name__)
app.secret_key = 'shikha'


@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/loginpage')
def loginpage():
    return render_template("login.html")
    

@app.route('/signuppage')
def sign():
    return render_template("SIGNUP.html")

    
@app.route('/signup', methods =['POST','GET'])
def signup():
    flag = False
    if request.method == "POST":
        user=request.form["uname"]
        password=request.form["psw"]
        query="""SELECT USERNAME,PASSWORD FROM signup;""" 
        mycursor.execute(query)
        row=mycursor.fetchall()
        for elem in row:
            if elem[0] == user:
                flag = True
                break
        if flag == True:
            return render_template("SIGNUP.html",user=user)
        else:
            mycursor.execute("INSERT INTO signup (USERNAME,PASSWORD) values (%s,%s)",(user,password)) 
            dbConn.commit()
            return render_template("login.html")
        

@app.route('/login_user', methods =['POST','GET'])
def login():
    flag = False
    user =request.form["username"]
    password =request.form["paswd"]
    query="""SELECT USERNAME,PASSWORD FROM signup;""" 
    mycursor.execute(query)
    row=mycursor.fetchall()
    for elem in row:
        if elem[0] == user and elem[1] == password:
             flag = True
             break 
    if flag == True:
        session['username'] = user
        mycursor.execute("SELECT * FROM city")
        myresult=mycursor.fetchall()
        new_city = list()
        for elem in myresult:
            new_city.append(elem)
        return render_template("myhome.html",new_city = new_city)
    else:
        return render_template("login.html",user=user)


@app.route('/home', methods =['POST','GET'])
def home():
    if 'username' in session:
        if request.method == 'POST':
            mycursor.execute("SELECT * FROM city")
            myresult=mycursor.fetchall()
            new_city = list()
            for elem in myresult:
                new_city.append(elem)
            return render_template("myhome.html",new_city = new_city)
    return render_template("welcome.html")

    
@app.route('/logout', methods =['POST','GET'])
def logout():
    if 'username' in session:
        session.pop('username', None)
        return render_template("logout.html")
        


@app.route('/theatre', methods =['POST','GET'])
def theatre():
     if 'username' in session:
         if request.method == 'POST':
             mycity = request.form['select_city']
             mycursor.execute("SELECT * FROM theatre where CITY_ID = %s",(mycity,))
             myresult=mycursor.fetchall()
             new_theatre = list()
             for elem in myresult:
                new_theatre.append(elem)
             mycursor.execute("SELECT * FROM city where CITY_ID = %s",(mycity,))
             cityresult=mycursor.fetchall()
             new_city = list()
             for element in cityresult:
                new_city.append(element)
             session['user_city'] = new_city
             mycursor.execute("SELECT * FROM day")
             result=mycursor.fetchall()
             new_day = list()
             for elem in result:
                new_day.append(elem)
             return render_template("theatres.html",new_theatre = new_theatre, new_city = new_city, new_day = new_day)
     return render_template("welcome.html")


@app.route('/movie', methods =['POST','GET'])
def movie():
     if 'username' in session:
         if request.method == 'POST':
             user_city = session['user_city']
             mytheatre = request.form['select_theatre']
             myday = request.form['select_day']
             mycursor.execute("SELECT * FROM mov_details where THEATRE_ID = %s and DAY = %s",(mytheatre,myday,))
             myresult=mycursor.fetchall()
             my_movie = list()
             for elem in myresult:
                my_movie.append(elem)
             mycursor.execute("SELECT * FROM theatre where THEATRE_ID = %s",(mytheatre,))
             theatre_result=mycursor.fetchall()
             new_theatre = list()
             for element in theatre_result:
                new_theatre.append(element)
             session['user_theatre'] = new_theatre
             session['theatreid'] = mytheatre
             mycursor.execute("SELECT * FROM day where DAY_ID = %s",(myday,))
             result=mycursor.fetchall()
             new_day = list()
             for elem in result:
                new_day.append(elem)
             session['user_day'] = new_day
             session['dayid'] = myday
             return render_template("movies.html",user_city = user_city ,my_movie = my_movie, new_theatre = new_theatre, new_day = new_day)
     return render_template("welcome.html")


@app.route('/timing', methods =['POST','GET'])
def time():
     if 'username' in session:
         if request.method == 'POST':
             user_city = session['user_city']
             user_theatre = session['user_theatre']
             user_day = session['user_day']
             theatreid = session['theatreid'] 
             dayid = session['dayid']
             myid = request.form['select_movie_id']
             session['movieid'] = myid
             mycursor.execute("SELECT * FROM movie where movie_id = %s ",(myid,))
             myresult=mycursor.fetchall()
             new_movie = list()
             for elem in myresult:
                 new_movie.append(elem)
             mycursor.execute("SELECT * FROM MOV_DETAILS where THEATRE_ID = %s and DAY = %s and  MOVIE_ID = %s ",(theatreid,dayid,myid,))
             cursor=mycursor.fetchall()
             time = list()
             for elem in cursor:
                 time.append(elem)
             return render_template("timings.html",time = time,new_movie = new_movie ,user_theatre = user_theatre, user_day = user_day , user_city = user_city)
     return render_template("welcome.html")


@app.route('/seat', methods =['POST','GET'])
def seatinfo():
     if 'username' in session:
         if request.method == 'POST':
             mytime = request.form['info']
             session['time'] = mytime
            #  print(mytime)
             theatreid = session['theatreid'] 
             dayid = session['dayid']
             movieid =  session['movieid']
             mycursor.execute("SELECT BOOK_SEAT FROM MOV_DETAILS where THEATRE_ID = %s and DAY = %s and MOVIE_ID = %s and TIME_ID = %s",(theatreid,dayid,movieid, mytime,))
             result=mycursor.fetchall()
             new_seat = int(result[0][0])
             mycursor.execute("SELECT SEATCOUNT FROM theatre where THEATRE_ID = %s",(theatreid,))
             row=mycursor.fetchall()
             totalseat = int(row[0][0])
             avail_seat = totalseat - new_seat
             session['availseat'] = avail_seat
             mycursor.execute("SELECT * FROM theatre where THEATRE_ID = %s",(theatreid,))
             myresult=mycursor.fetchall()
             new_seatprice = list()
             for elem in myresult:
                new_seatprice.append(elem)
             return render_template("seat_info.html", avail_seat = avail_seat , new_seatprice = new_seatprice)
     return render_template("welcome.html")

# 
@app.route('/booking', methods =['POST','GET'])
def book():
     if 'username' in session:
         if request.method == 'POST':
             user_city = session['user_city']
             user_theatre = session['user_theatre']
            #  print(user_theatre[0])
             user_day = session['user_day']
             myid = session['movieid']
             theatreid = session['theatreid'] 
             dayid = session['dayid']
             mycursor.execute("SELECT * FROM movie where movie_id = %s ",(myid,))
             myresult=mycursor.fetchall()
             new_movie = list()
             for elem in myresult:
                  new_movie.append(elem)
             mycursor.execute("SELECT * FROM MOV_DETAILS where THEATRE_ID = %s and DAY = %s and  MOVIE_ID = %s ",(theatreid,dayid,myid,))
             cursor=mycursor.fetchall()
             time = list()
             for elem in cursor:
                 time.append(elem)
            #  session['mytime'] = time
             seats = request.form["select_seat"]
             seat2 = int(seats)
             session['myseat'] = seat2
             seatprice = request.form["seatprice"]
             seatprice2 = int(seatprice)
             price = seat2*seatprice2
             avail_seat = session['availseat']
             mycursor.execute("SELECT * FROM theatre where THEATRE_ID = %s",(theatreid,))
             myresult=mycursor.fetchall()
             new_seatprice = list()
             for elem in myresult:
                 new_seatprice.append(elem)
             if avail_seat < seat2:
                 return render_template("seat_info.html", avail_seat = avail_seat, new_seatprice = new_seatprice,myid = myid)
             elif seat2 == 0:
                 return render_template("seat_info.html", avail_seat = avail_seat, new_seatprice = new_seatprice,theatreid =  theatreid)
             else:
                 return  render_template("price.html", price = price,time = time,new_movie = new_movie ,user_theatre = user_theatre, user_day = user_day , user_city = user_city)
     return render_template("welcome.html")


@app.route('/price', methods =['POST','GET'])
def prices():
     if 'username' in session:
         if request.method == 'POST':
              price = request.form["totalprice"]
              session['price'] = price
              return render_template("payment.html")
     return render_template("welcome.html")
   

@app.route('/payment', methods =['POST','GET'])
def pay():
     if 'username' in session:
         if request.method == 'POST':
             user = session['username']
             price = session['price']
             amount = request.form["amount"]
             theatreid = session['theatreid'] 
             mycursor.execute("SELECT THEATRE_NAME FROM theatre where THEATRE_ID = %s",(theatreid,))
             myresult=mycursor.fetchall()
             myresult2 = myresult[0][0]
             movieid =  session['movieid']
             mycursor.execute("SELECT MOVIE_NAME FROM MOVIE where MOVIE_ID = %s",(movieid,))
             result=mycursor.fetchall()
             result2 = result[0][0]
             dayid = session['dayid']
             mycursor.execute("SELECT DAY FROM DAY where DAY_ID = %s",(dayid,))
             res=mycursor.fetchall()
             res2 = res[0][0]
             time = session['time']
             myseat = session['myseat']
             if price <= amount:
                 mycursor.execute("SELECT BOOK_SEAT FROM MOV_DETAILS where THEATRE_ID = %s and DAY = %s and MOVIE_ID = %s and TIME_ID = %s",(theatreid,dayid,movieid,time,))
                 result=mycursor.fetchall()
                 seat = int(result[0][0])+myseat
                 mycursor.execute("UPDATE MOV_DETAILS SET BOOK_SEAT = %s WHERE THEATRE_ID = %s and DAY = %s and MOVIE_ID = %s and TIME_ID = %s", (seat,theatreid,dayid,movieid,time,))
                 dbConn.commit()
                 mycursor.execute("INSERT INTO BOOKING (USERNAME,THEATRE_Name,MOVIE_NAME,DAY,TIMING, NO_OF_SEATS_BOOKED) values (%s,%s,%s,%s,%s,%s)",(user,myresult2,result2,res2,time,myseat,)) 
                 dbConn.commit()
                 return render_template("thanx.html",user = user)
             else:
                 return render_template("payment.html",amount = amount)
     return render_template("welcome.html")
   
         
        
@app.route('/details', methods =['POST','GET'])
def det():
     if 'username' in session:
         if request.method == 'POST':
             user = session['username']
             mycursor.execute("SELECT USERNAME,THEATRE_Name,MOVIE_NAME,DAY,TIMING, NO_OF_SEATS_BOOKED FROM BOOKING where USERNAME = %s",(user,))
             result = mycursor.fetchall()
             details = list()
             for elem in result:
                 details.append(elem)
             return render_template("thanx.html",details = details)
     return ("welcome.html")        
             

# @app.route('/cancel', methods =['POST','GET'])
# def can():
#    if 'username' in session:
#        if request.method == 'POST':
#            if         
