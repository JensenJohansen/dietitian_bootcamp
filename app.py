import calendar
import datetime
import os
import random
import re
import warnings
from _datetime import datetime

import MySQLdb.cursors
import playsound
import speech_recognition as sr
import wikipedia
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from gtts import gTTS

import connect

warnings.filterwarnings('ignore')
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dietician'

# Initialize MySQL
mysql = MySQL(app)


class Person:
    name = ''
    gender = ''
    age = 0
    height = ''
    weight = ''
    exercise = ''
    work_type = ''
    region = ''
    password = ''
    BMI = 0.0
    BMI_ID = 0
    shifter = 1

    def set_name(self, name):
        self.name = name

    def set_height(self, height):
        self.height = height

    def set_weight(self, weight):
        self.weight = weight

    def set_region(self, region):
        self.region = region

    def set_BMI(self, BMI):
        self.BMI = BMI

    def set_password(self, password):
        self.password = password

    def set_bmi_id(self, BMI_ID):
        self.BMI_ID = BMI_ID

    def set_age(self, age):
        self.age = age

    def set_gender(self, gender):
        self.gender = gender

    def set_exercise(self, exercise):
        self.exercise = exercise

    def set_work_type(self, work_type):
        self.work_type = work_type

    def set_shifter(self, shifter):
        self.shifter = shifter


person_object = Person()

msg =''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pythonlogin/vc', methods=['GET', 'POST'])
def vc():
    def vca():
        def there_exists(terms):
            for term in terms:
                if term in text:
                    return True

        def inserting_user_information(name, password, bmi, bmi_id, age, gender, exercise, work_type, region):
            my_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql_string = 'INSERT INTO user_table (Username, Password, user_bmi, BMI_ID, age, gender, exercises, ' \
                         'workType, region) values ("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}");'.format(
                name,
                password,
                bmi, bmi_id, age, gender, exercise, work_type, region)
            my_cursor.execute(sql_string)
            mysql.connection.commit()
            speak(f"Welcome {name}, you have completely been registered!")

        def recordAudio(starter):
            global msg
            with sr.Microphone() as source:
                r = sr.Recognizer()
                speak(starter)
                msg = starter
                audio = r.listen(source)
                data = ''
            try:
                data = r.recognize_google(audio)
                msg = ('you said: ' + data)
            except sr.UnknownValueError:
                msg = "Sorry! I didn't understand! "
            except sr.RequestError as e:
                msg = "errors occurred can't continue!"
            return data

        # get string and make a audio file to be played
        def speak(audio_string):
            tts = gTTS(text=audio_string, lang='en-tz')  # text to speech(voice)
            r = random.randint(1, 20000000)
            audio_file = 'audio' + str(r) + '.mp3'
            tts.save(audio_file)  # save as mp3
            playsound.playsound(audio_file)  # play the audio file
            global msg
            msg = f"dietitian: {audio_string}"  # print what app said
            os.remove(audio_file)

            # return render_template('mic1.html', hii=msg)

        # food scheduling method
        def food_scheduling(bmi_id, time):
            my_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql_string = f"SELECT FOOD_NAME,AMOUNT,FOOD_TIME FROM food_table WHERE BMI_ID ='{bmi_id}'"
            my_cursor.execute(sql_string)
            records = my_cursor.fetchall()
            foods = []
            for row in records:
                foods.append(
                    f"Food name is {row['FOOD_NAME']} , amount of  {row['AMOUNT']} and this food can be eaten at {row['FOOD_TIME']}")

            food_schedule = []
            for food in foods:
                if time in food:
                    food_schedule.append(food)
            speak(f"You can eat one or two or both of the suggested food as your meal for {time} ")
            speak(random.choice(food_schedule))
            speak(random.choice(food_schedule))
            speak(random.choice(food_schedule))

        register = False

        while True:

            if person_object.shifter == 1 and not register:
                starter = "Hello, please sign in. First say your name or say am not registered to register"
            elif person_object.shifter == 2 and not register:
                starter = f'Okay {person_object.name}, Please say your password'
            elif person_object.shifter == 1 and register:
                starter = 'Okay, am your dietitian and will guide you through the Registration.what is your name?'
            else:
                starter = f'{person_object.name}, speak.'

            text = recordAudio(starter)
            response = ''

            if there_exists(
                    ["not registered", "I'm not registered", "I have not registered", "I haven't registered"]):
                register = True

            if there_exists(['my name is']) and not register:
                person_object.name = text.split("is")[-1].strip()

                person_object.shifter = 2

            if there_exists(["my password is"]) and not register:
                person_object.password = str(text.split("is")[-1].strip())
                print("User password " + person_object.password)
                my_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql_string = 'select * from user_table where Username=%s and Password=%s'
                var = (person_object.name, person_object.password)
                my_cursor.execute(sql_string, var)
                user_information = my_cursor.fetchone()
                print(user_information)
                try:
                    if str(user_information['Username']).lower() == str(person_object.name).lower() and \
                            user_information['Password'] == person_object.password:
                        person_object.BMI_ID = user_information['BMI_ID']
                        person_object.shifter = 0
                        register = True
                        speak(
                            f'Welcome {person_object.name}, what food schedule do you want? breakfast, lunch or dinner')
                except TypeError:
                    speak("sorry! you have entered wrong username or password")
                """ except KeyError:
                    speak("Key error has occurred")"""

            # getting the person name
            if there_exists(["my name is"]) and person_object.shifter == 1 and register:
                person_name = text.split("is")[-1].strip()
                speak(f"okay {person_name}, please enter now your gender, example, male or female")
                person_object.set_name(person_name)
                person_object.shifter = 2

            # getting person gender
            if there_exists(["my gender is"]) and person_object.shifter == 2 and register:
                person_gender = text.split("is")[-1].strip()
                speak(f"okay {person_object.name}, i will remember that.Please say your age in years")
                person_object.set_gender(person_gender)
                person_object.shifter = 3

            # getting person age
            if there_exists(["my age is"]) and person_object.shifter == 3 and register:
                person_age = text.split("is")[-1].strip()
                speak(f"okay {person_object.name}, i will remember that.Please say your height in meters")
                person_object.set_age(person_age)
                person_object.shifter = 4

            # getting the person height
            if there_exists(["my height is"]) and person_object.shifter == 4 and register:
                person_height = text.split("is")[-1].strip()
                speak(f"okay {person_object.name}, i will remember that, please enter now your weight in kilograms ")
                person_object.set_height(person_height)
                person_object.shifter = 5

            # getting the person weight
            if there_exists(["my weight is"]) and person_object.shifter == 5 and register:
                person_weight = text.split("is")[-1].strip()
                speak(
                    f"okay {person_object.name}, i will remember that.Please now say how frequent you do exercise, example "
                    f"often, rarely, never")
                person_object.set_weight(person_weight)
                person_object.shifter = 6

            # getting the person exercise
            if there_exists(["I do exercise"]) and person_object.shifter == 6 and register:
                person_exercise = text.split("exercise")[-1].strip()
                speak(
                    f"okay {person_object.name}, i will remember that, please say kind of work you are doing, example "
                    f"teacher, driver, farmer, student, none")
                person_object.set_exercise(person_exercise)
                person_object.shifter = 7

            # getting the person work_type
            if there_exists(["my work is", "i'm a", "i am a", "my job is"]) and person_object.shifter == 7 and register:
                person_job = text.split("is")[-1].strip()
                speak(f"okay {person_object.name}, i will remember that, please say region where you live")
                person_object.set_work_type(person_job)
                person_object.shifter = 8

            # getting the person region
            if there_exists(["my region is", "i'm from"]) and person_object.shifter == 8 and register:
                person_region = text.split("is")[-1].strip()
                speak(f"okay {person_object.name}, i will remember that, please say your password")
                person_object.set_region(person_region)
                person_object.shifter = 9

            # saying the password
            if there_exists(["my password is"]) and person_object.shifter == 9 and register:
                person_password1 = text.split("is")[-1].strip()
                speak(f"okay {person_object.name}, congratulations, you have finished feeding data.")
                person_object.set_password(person_password1)
                inserting_user_information(person_object.name, person_object.password, person_object.BMI,
                                           person_object.BMI_ID, person_object.age, person_object.gender,
                                           person_object.exercise,
                                           person_object.work_type, person_object.region)
                person_object.shifter = 0

            # calculating and serving the bmi value
            if person_object.shifter == 6 and register:
                height = float(person_object.height)
                weight = float(person_object.weight)
                bmi = weight / height ** 2
                person_object.set_BMI(bmi)
                if bmi < 18.5:
                    person_object.set_bmi_id(1)
                if 18.5 <= bmi <= 24.9:
                    person_object.set_bmi_id(2)
                if 25.0 <= bmi <= 29.9:
                    person_object.set_bmi_id(3)
                if bmi >= 30.0:
                    person_object.set_bmi_id(4)

            # getting food schedule
            if there_exists(["I want my food schedule for", "i want schedule for", "food for",
                             "please give me a schedule for",
                             "give a schedule for"]) and person_object.shifter == 0 and register:
                time = text.split("for")[-1].strip()
                food_scheduling(person_object.BMI_ID, time)

            # quiting
            if there_exists(
                    ["exit", "quit", "goodbye", "thanks see you", "thank you i love it", "thanks for your service",
                     "thank you for your service", "thank you see you", "see you", "thank you"]):
                speak(f"You a welcome {person_object.name}, see you later")
                person_object.shifter=1
                register = False
                logout()
                break

    if request.method == 'POST':
        global msg
        ree = msg
        return render_template('mic1.html', resp=vca(), msg=ree)
    else:
        return render_template('mic1.html', msg=msg)


# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = 'SELECT * FROM user_table WHERE Username =%s AND Password = %s'
        var = (username, password)
        cursor.execute(sql, var)
        # Fetch one record and return result
        user = cursor.fetchone()

        # If account exists in accounts table in out database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user['userID']
            session['username'] = user['Username']
            session['age'] = user['age']
            session['BMI'] = user['user_bmi']
            session['BMI_ID'] = user['BMI_ID']
            session['gender'] = user['gender']
            session['exercises'] = user['exercises']
            session['workType'] = user['workType']
            session['region'] = user['region']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template('index.html', msg=msg)
    else:
        return redirect(url_for('index'))


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    msg = 'logged out successfully'
    # Redirect to login page
    return render_template('index.html', msg=msg)


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST
# requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and \
            'height' in request.form and 'weight' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        age = int(request.form['age'])
        gender = request.form['gender']
        exercises = request.form['exercises']
        workType = request.form['workType']
        region = request.form['region']
        bmi = float(weight / pow(height, 2))
        bmi_id = int(connect.bmi_id(bmi))
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_table WHERE Username = %s', [username])
        user = cursor.fetchone()
        # If account exists show error and validation checks
        if user:
            msg = 'Account already exists!'
            return redirect(url_for("login"))
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
            return render_template("register.html", msg=msg)
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql1 = 'INSERT INTO user_table(Username,Password,user_bmi, BMI_ID,age,gender,exercises,workType,' \
                   'region) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) '
            var = (username, password, bmi, bmi_id, age, gender, exercises, workType, region)
            cursor.execute(sql1, var)
            mysql.connection.commit()
            msg = "successfully registered!"
            return render_template('register.html', msg=msg)

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        junior=str(session['username'])
        return render_template('home.html', username=junior.capitalize())
    else:
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT userID,Username,age,user_bmi,exercises,workType,region,BMI_DESCRIPTION FROM '
                       'user_table,bmi_table WHERE userID = %s AND bmi_table.BMI_ID=user_table.BMI_ID',
                       [session['id']])
        user = cursor.fetchone()
        session["bmi_desc"]=user["BMI_DESCRIPTION"]
        # Show the profile page with account info
        return render_template('profile.html', user=user)
    else:
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))


@app.route('/pythonlogin/schedule', methods=["POST", "GET"])
def schedule():
    if 'loggedin' in session:
        if request.method == "POST":
            if request.form.get("Breakfast"):
                time = "breakfast"

            elif request.form.get("Lunch"):
                time = "lunch"
            elif request.form.get("Dinner"):
                time = "dinner"
            else:
                time = ""
            while True:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM food_table WHERE BMI_ID = %s', [session['BMI_ID']])
                food_sched = cursor.fetchall()
                foods = []
                for row in food_sched:
                    foods.append(
                        f"{row['FOOD_NAME']} , amount of  {row['AMOUNT']} and this food can be eaten at {row['FOOD_TIME']}")

                food_schedule = []
                for food in foods:
                    if time in food:
                        food_schedule.append(food)
                fd = f"You can eat one or two or both of the suggested food as your meal for {time.title().upper()} "
                f = random.choice(food_schedule)
                s = random.choice(food_schedule)
                t = random.choice(food_schedule)

                return render_template("food_sch.html", fd=fd, f=f, s=s, t=t)
        return render_template("food_sch.html")

    else:
        return redirect(url_for('login'))


@app.route('/pythonlogin/chat', methods=['POST', 'GET'])
def chatpallete():
    txt = ''
    if 'loggedin' in session:
        return render_template('chatpallete.html', responsee=txt)


if __name__ == '__main__':
    app.run()
