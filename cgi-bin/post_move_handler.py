#!/usr/bin/python
import cgi
print('Content-Type: text/html\n\n')
#print()
import cgitb
import sqlite3

cgitb.enable()     # for troubleshooting

def main():

    form = cgi.FieldStorage()
    fields = {}
    for key in form.keys():
        fields[key] = str(form.getvalue(str(key)))

    err = check_form_integrity(fields)
    if (err != 0):
        print("<font color='red'><b><br>Error in form entry, job not finished.</font></b><br><br>")
        return

    date = add_date(fields)
    date = '"' + str(date) + '"'

    db, db_conn = connect_to_DB()
    jobs = []

    #for row in db.execute('SELECT * FROM active_jobs WHERE date = ' + str(date) + " and client_name = " + str(fields['client_name'])):
    for row in db.execute('SELECT * FROM active_jobs WHERE date = ? and client_name = ?', [date, fields['client_name']]):
        jobs.append(row)

    if not jobs:
        print("<font color='red'><b><br>Specified job not found.</font></b><br><br>")
        return

    #TODO: handle if mult jobs and if job DNE
    #col_names = [description[0] for description in db.description] #TODO: wtf is this?
    sql_cols = ''
    first=True
    for name in col_names:
        if first == False: sql_cols += ','
        else: first=False
        sql_cols += name
    sql_cols += 'actual_time, post_comments'

    sql_vals = ''
    first = True
    for vals in jobs[0]:
        if first == False: sql_cols += ','
        else: first=False
        sql_vals += name        
    sql_vals += ',' + str(fields['actual_time']) + ',' + str(fields['post_comments'])

    db.execute('INSERT INTO active_jobs (' + str(sql_cols) + ') VALUES (' + str(sql_vals) + ')')
    db.execute('DELETE FROM active_jobs WHERE active_jobs WHERE date = ' + str(date) + " and client_name = " + str(fields['client_name']))

    url = 'http://mmmoving.weebly.com/finished-move.html'
    print ('<meta http-equiv="refresh" content="0;url=%s" />' % url)
    print ('<body>Redirecting... <a href="%s">Click here if you are not redirected</a></body>' % url)
    print ('</html>')

def save_exit_DB(conn):
    conn.commit()
    conn.close()

def connect_to_DB ():
    path = '/home/2014/choppe1/public_html/mmmoving.db' #i assume full path nec
    conn = sqlite3.connect(path)
    db = conn.cursor()

    return db, conn

def add_date(fields):

    day = int(fields['day'])
    if (day < 10): day_str = "0" + str(day)
    else: day_str = str(day)
    year = '2017'
    date = year + "-" + str(fields['month']) + "-" + day_str
    fields['date']=date
    return date
    

def check_form_integrity(fields):
    err = 0

    not_nulls = ['client_name']
    not_nones = ['month', 'day', 'actual_time']
    
    for title in not_nulls:
        if (title not in fields.keys()):
            print("<font color='red'> Error: " + title + " must not be left empty.</font><br>")
            err = 1 
    for title in not_nones:
        if (fields[title] == 'none'):
            print("<font color='red'>Error: must pick a value for " + title + ".</font><br>")
            err = 1

    return err


main()
