from flask import Flask, render_template, request, flash
import mysql.connector
from random import randint
import decimal
mydb = mysql.connector.connect(user='root', password='rvr1378rvr1378',
                               host='127.0.0.1', database='university',
                               auth_plugin='mysql_native_password')
mycursor = mydb.cursor()
buffcursor = mydb.cursor()
app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = 'asrtarstaursdlarsn'
student = []
D = decimal.Decimal


@app.route('/StudentInfo')
def StudentInfo():
    isempty = 0
    test_list = []
    mylist = []
    sql = "select * from takes where id=%s"

    sql_id = (student[0],)
    mycursor.execute(sql, sql_id)
    res = mycursor.fetchall()

    if res == []:
        isempty = 0
    else:
        i = 0
        for row2 in res:
            i = i + 1
            isempty = i
    sql = "select title from course where course_id=%s"
    for x in res:
        course_id = x[1]
        sql_course = (course_id,)
        mycursor.execute(sql, sql_course)
        addlist = mycursor.fetchall()
        test_list.append(addlist)

    for x in test_list:
        mylist.append(x[0][0])

    return render_template('StudentLogin.html', name=student[1], mylist=mylist, IsEmpty=isempty)


@app.route('/signout')
def signout():
    student.clear()
    return render_template('home.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/scores')
def scores():
    mylist = []
    sql = "select * from takes where id = %s"
    sql_user = (student[0], )
    mycursor.execute(sql, sql_user)
    res = mycursor.fetchall()

    for row in res:
        sql = "select title from course where course_id=%s"
        course_id = (row[1], )
        mycursor.execute(sql, course_id)
        title_res = mycursor.fetchall()

        mylist.append((title_res[0][0], row[5]))

    return render_template('scores.html', name=student[1], mylist=mylist)


@app.route('/StudentLogin')
def StudentLogin(name, mylist, IsEmpty):
    return render_template('StudentLogin.html')


@app.route('/selectunit')
def selectunit():
    list = []
    department = (student[3],)
    sql = "select title,course_id from course where dept_name = %s"
    mycursor.execute(sql, department)
    res = mycursor.fetchall()
    for row in res:
        course_id = (student[0], row[1])
        sql = "select * from takes where id=%s and course_id = %s"
        mycursor.execute(sql, course_id)
        res = mycursor.fetchall()
        if res != []:
            status = "disabled"
        else:
            status = None
        list_append = [row[0], status, row[1]]
        list.append(list_append)
    return render_template('selectunit.html', name=student[1], list=list)


@app.route("/login/", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        user = request.form['Student_Number']
        password = request.form['Password']
        sql = "select * from student where id = %s"
        Sql_user = (user, )
        mycursor.execute(sql, Sql_user)
        myresult = mycursor.fetchall()
        if myresult == []:
            flash('Invalid username or password', 'danger')
            return render_template("home.html")
        else:
            for row in myresult:
                if(row[2] == password):
                    j = 0
                    while j < 4:
                        student.append(row[j])
                        j = j+1
                    print(student)
                    mylist = []
                    test_list = []
                    sql = "select * from takes where id=%s"
                    sql_id = (row[0], )
                    mycursor.execute(sql, sql_id)
                    res = mycursor.fetchall()

                    if res == []:
                        IsEmpty = 0
                    else:
                        i = 0
                        for row2 in res:
                            i = i+1
                        IsEmpty = i
                    sql = "select title from course where course_id=%s"
                    for x in res:
                        course_id = x[1]
                        sql_course = (course_id, )
                        mycursor.execute(sql, sql_course)
                        addlist = mycursor.fetchall()
                        test_list.append(addlist)
                    for x in test_list:
                        mylist.append(x[0][0])
                    return render_template("StudentLogin.html", name=row[1], mylist=mylist, IsEmpty=IsEmpty)
                else:
                    flash('Invalid username or password', 'warning')
                    return render_template("home.html")

    return render_template("home.html")


@app.route("/studentselectunit/", methods=['GET', 'POST'])
def studentselectunit():

    option = request.form['radio']
    sql = "select course_id,sec_id,semester,year from section where course_id = %s "
    section_id = (option, )
    mycursor.execute(sql, section_id)
    section_res = mycursor.fetchall()
    sql = "insert into takes values (%s, %s, %s, %s, %s,%s)"
    score_random = randint(1, 28)
    if score_random < 4:
        student_score = "A+"
    if 4 <= score_random < 7:
        student_score = "A"
    if 7 <= score_random < 10:
        student_score = "A-"
    if 10 <= score_random < 13:
        student_score = "B+"
    if 13 <= score_random < 16:
        student_score = "B"
    if 16 <= score_random < 19:
        student_score = "B-"
    if 19 <= score_random < 22:
        student_score = "C+"
    if 22 <= score_random < 25:
        student_score = "C"
    if 25 <= score_random < 28:
        student_score = "C-"
    if score_random == 28:
        student_score = "0"

    sql_insert = (student[0], section_res[0][0], section_res[0][1],
                  section_res[0][2], int(section_res[0][3]), student_score)
    mycursor.execute(sql, sql_insert)
    mydb.commit()
    list = []
    department = (student[3],)
    sql = "select title,course_id from course where dept_name = %s"
    mycursor.execute(sql, department)
    res = mycursor.fetchall()
    for row in res:
        course_id = (student[0], row[1])
        sql = "select * from takes where id=%s and course_id = %s"
        mycursor.execute(sql, course_id)
        res = mycursor.fetchall()
        if res != []:
            status = "disabled"
        else:
            status = None
        list_append = [row[0], status, row[1]]
        list.append(list_append)
    return render_template('selectunit.html', name=student[1], list=list)


if __name__ == '__main__':
    app.run(debug=True)
