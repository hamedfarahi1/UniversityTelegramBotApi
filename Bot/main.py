import mysql.connector
import telebot
from telebot import types
from random import randint
import time
import Captcha

mydb = mysql.connector.connect(user='root', password='********',
                              host='127.0.0.1', database='university',
                              auth_plugin ='mysql_native_password')
mycursor = mydb.cursor()
buffcursor = mydb.cursor()

id = ""
bot = telebot.TeleBot(token="851591439:AAFCIkMGZcMxUtjQR-uUsBWVk2w-0Ds4yLM")


class ID:
    staticVariable = ""
    auth = False
    cap = ""
    capAuth = False
    canLogin = False


student_id = ID()


@bot.message_handler(func=lambda q: q.text.lower() == "/login")
def CaptchaAuth(message):
    captcha = Captcha.create_random_captcha_text()
    image = open(Captcha.create_image_captcha(captcha), 'rb')
    bot.send_photo(message.chat.id, image)
    bot.send_message(message.chat.id, "Enter Captcha  /" + captcha+"_")
    student_id.cap = captcha
    student_id.capAuth = True


@bot.message_handler(func=lambda q: '_' in q.text)
def CaptchaEnter(message):
    if student_id.capAuth:
        if message.text[1:].lower() == student_id.cap.lower()+'_':
            bot.reply_to(message, "Now You Can log in  (ex:  @ID:password )")
            student_id.canLogin = True
        else:
            bot.reply_to(message, "Wrong Captcha")
    else:
        bot.reply_to(message, "First Enter captcha")


@bot.message_handler(func=lambda message: '@' == message.text[0])
def auth(message):
    if student_id.canLogin:
        if not student_id.auth:
            sql = "select password from student where id=%s"
            s_id = message.text[1:6]
            sql_id = (s_id,)
            mycursor.execute(sql, sql_id)
            myresult = mycursor.fetchall()
            if myresult is not None:
                for row in myresult:
                    if message.text[7:] == row[0]:
                        bot.reply_to(message, "login successFully")
                        student_id.auth = True
                        student_id.staticVariable = s_id
                        return
                    bot.reply_to(message, "Invalid PassWord")
                    return
            bot.reply_to(message, "Invalid ID")
            del sql
            del s_id
            del sql_id
            del myresult

        else:
            bot.reply_to(message, "First LogOut")
    else:
        bot.send_message(message.chat.id, "are you a bot?!  /login")


@bot.message_handler(func=lambda message: message.text == "/logout")
def logout(message):
    if student_id.auth:
        student_id.auth = False
        student_id.staticVariable = None
        student_id.canLogin = False
        student_id.cap = None
        student_id.capAuth = False
        bot.reply_to(message, "Logout successfully")

    else:
        bot.reply_to(message, "Not LogIn")


@bot.message_handler(func=lambda message: message.text.lower() == "/lessons")
def get_hrefs(message):
    if student_id.auth:
        buttons = []
        sql = "select title,course_id from course where dept_name=(select dept_name from student where id=%s)"
        sql_id = (student_id.staticVariable,)
        mycursor.execute(sql, sql_id)
        myresult = mycursor.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for row in myresult:
            buttons.append(types.InlineKeyboardButton(
                text=row[0], callback_data="$$" + row[1]))
        keyboard.add(*buttons)
        bot.reply_to(message, "your lessons", reply_markup=keyboard)

        del keyboard
        del sql
        del sql_id
        del myresult
        return
    bot.reply_to(message, "Not Login")


@bot.message_handler(func=lambda q: q.text.lower() == "/marks")
def marks(message):

    if student_id.auth:
        stu_id = student_id.staticVariable
        mycursor.execute(
            '''select course_id,year,grade from takes where id="{}"'''.format(stu_id))
        myresult = mycursor.fetchall()
        if len(myresult) != 0:
            for row in myresult:
                mycursor.execute(
                    '''select title from course where course_id="{}"'''.format(str(row[0])))
                myres = mycursor.fetchall()
                for ro in myres:
                    title = ro[0]
                bot.send_message(message.chat.id,
                                 "Title: {0:20}       Year: {1}       Grade:    {2:2}".format(title, row[1], row[2]))
        else:
            bot.send_message(message.chat.id,"No Course Detect")

    else:
        bot.send_message(message.chat.id, "Not Login")


@bot.callback_query_handler(lambda q: q.message.chat.type == "private" and ("$$" in str(q.data) or "&&" in str(q.data)))
def private_query(query):
    if student_id.auth:
        if "$$" in str(query.data):
            sql = "select course_id from course where title=%s"
            st_id = student_id.staticVariable
            sql = "select course_id,sec_id,semester,year from section where course_id = %s "
            course_id = (str(query.data)[2:9],)
            mycursor.execute(sql, course_id)
            myresult = mycursor.fetchall()
            sec_exist = False
            for row in myresult:
                c_id = row[0]
                s_id = row[1]
                sem = row[2]
                year = row[3]
                sec_exist = True
            mycursor.execute('''select course_id from takes where id="{0}"'''.format(st_id))
            myres = mycursor.fetchall()
            isTake = False
            for row in myres:
                if str(row[0]) == str(query.data)[2:9]:
                    isTake = True
            if sec_exist and not isTake:
                mycursor.execute('''select tot_cred from student where ID="{0}"'''.format(st_id))
                myres = mycursor.fetchall()
                tot_cred = 0
                for row in myres:
                    mycursor.execute(
                        '''select credits from course where course_id="{0}"'''.format(str(query.data)[2:9]))
                    tot = mycursor.fetchall()
                    for r in tot:
                        tot_cred = r[0] + row[0]
                mycursor.execute('''update student set tot_cred={0} where id="{1}"'''.format(str(tot_cred), st_id))
                # sql = "insert into takes values (%s, %s, %s, %s, %s,%s)"
                score = str(chr(randint(65, 68)))
                sql_q = '''insert into takes values ("{0}", "{1}", "{2}", "{3}", {4},"{5}")'''.format(st_id,
                                                                                                      c_id, s_id, sem,
                                                                                                      int(year), score)
                # scores = ["A", "B", "C", "0", "A+", "B+", "C+", "A-", "B-", "C-"]
                mycursor.execute(sql_q)
                mydb.commit()
                # sql_id = (st_id)
                mycursor.execute(
                    '''select * from takes where id="{}"'''.format(st_id))
                myresult = mycursor.fetchall()
                buttons = []
                keyboard = types.InlineKeyboardMarkup()
                for row in myresult:
                    txt = str(row[0]) + " -- " + str(row[1]) + " -- " + str(row[2]) + \
                          " -- " + str(row[3]) + " -- " + str(row[4]) + " -- " + str(row[5])
                    buttons.append(types.InlineKeyboardButton(
                        text=txt, callback_data="&&" + str(row[0])))
                keyboard.add(*buttons)
                bot.reply_to(query.message, reply_markup=keyboard)
                del keyboard
                # del sql
                # del course_id
                # del buttons
                # del st_id
                # del c_id
                # del s_id
                # del sem
                # del year
                # del myresult
                # del score
                # del scores
                # del sql_id
                # del sql_q
                # del txt
            else:
                bot.reply_to(query.message, "lesson fails or was took")
        elif ("&&" in query.data):
            stu_id = query.data[2:7]
            mycursor.execute(
                '''select course_id,year,grade from takes where id="{}"'''.format(stu_id))
            myresult = mycursor.fetchall()
            for row in myresult:
                mycursor.execute(
                    '''select title from course where course_id="{}"'''.format(str(row[0])))
                myres = mycursor.fetchall()
                for ro in myres:
                    title = ro[0]

            bot.send_message(query.message.chat.id,
                             "Title: {0:20}       Year: {1}       Grade:    {2:2}".format(title, row[1], row[2]))
    else:
        bot.reply_to(query.message,"not login")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            bot.stop_bot()
            time.sleep(5)
            print(ex)
