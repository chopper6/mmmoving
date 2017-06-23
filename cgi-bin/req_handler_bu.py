#!/usr/bin/python
import cgi
print('Content-Type: text/html\n\n')
#print()
import cgitb
import sqlite3
#sys.path.insert(0, '/home/2014/choppe1/public_html/mmmoving/cgi-bin')
#import scheduler

cgitb.enable()     # for troubleshooting

def main():

    #print ("<html><head><title>Processing Move</title></head>\n")
    #print ("Location:http://mmmoving.weebly.com/")
    #print('<body>\n')
    form = cgi.FieldStorage()
    fields = {}
    for key in form.keys():
        fields[key] = str(form.getvalue(str(key)))

    err = check_form_integrity(fields)
    if (err != 0):
        print("<font color='red'><b><br>Error in form entry, job not scheduled.</font></b><br><br>")
        return

    # adding fields, ASSUMES 8am-8pm work days
    date = add_date(fields)
    date = '"' + str(date) + '"'
    poss_intervals = derive_poss_intervals(fields)
    fields['poss_intervals'] = str(poss_intervals)

    db, db_conn = connect_to_DB()
    jobs = []
    for row in db.execute('SELECT id, poss_intervals FROM active_jobs WHERE date = ' + str(date)):
        jobs.append(row)
    #jobs.sort(key=lambda x: int(len(x[1])) #sort by num intervals

    # determine id (as latest +1)
    max_id_job =  [i for i in db.execute('SELECT id FROM active_jobs ORDER BY id DESC LIMIT 1')]
    if (max_id_job): new_id = int(max_id_job[0][0])+1
    else: new_id=0
    #print("<br>max id job = " + str(new_id) + "<br>")
    fields['id']=new_id
   
    new_job = [new_id, poss_intervals]
    jobs = [new_job] + jobs 
    hours = [-1 for i in range(8,21)] # again ASSUMES 8-8 work days
    #sched = scheduler.build (jobs, hours)
    sched = False #TODO: temp both above and below 1
	if (sched == True):

        cols = ', '.join(fields.keys())
        holders = ':'+', :'.join(fields.keys())
        query = 'INSERT INTO active_jobs (%s) VALUES (%s)' % (cols, holders)
        db.execute(query, fields)

        save_exit_DB(db_conn)
        url = 'http://mmmoving.weebly.com/request-succeed.html'

    else:
        url =  'http://mmmoving.weebly.com/request-failed.html'

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


def build_schedule (jobs, hours):
    # assumes jobs are sorted by min number of poss intervals
    # intervals is a list of avail slots
    # each job should have a list of poss intervals
    if not jobs: return hours #base case, hours is the schedule
    #print("<br><br>sched_exists(): jobs[0][1] = " + str(jobs[0][1]) + ". <br><br>")


    hour0 = 8
    intervals = str_intervals_to_list(jobs[0][1])
    job_id = int(jobs[0][0])
    for intrv in intervals:
        start, stop = intrv.split("-")
        start, stop = int(start), int(stop)
        free = True
        for i in range(start-hour0,stop-hour0): #CHECK off-by-one err
            if (hours[i] != -1): free = False
        if (free == True):
            hours2 = hours
            for i in range(start-hour0,stop-hour0): #CHECK off-by-one err
                hours2[i] = jobs_id
            sched = sched_exists(jobs[1:], hours2)

            if (sched): return sched #poss save sched instance as well?
    return False


def str_intervals_to_list(string):
    # assumes ['8-19']-<F12>
    string = string.replace('[','').replace(']','').replace("'",'')
    intrvs = string.split(',')
    return intrvs

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

    not_nulls = ['client_name', 'from_address', 'to_address', 'phone']
    not_nones = ['month', 'day', 'estim_time']
    
    for title in not_nulls:
        if (title not in fields.keys()):
            print("<font color='red'> Error: " + title + " must not be left empty.</font><br>")
            err = 1 
    for title in not_nones:
        if (fields[title] == 'none'):
            print("<font color='red'>Error: must pick a value for " + title + ".</font><br>")
            err = 1

    if ('phone' in fields.keys()):
        if (len(fields['phone'].strip()) != 10):
            print("<font color='red'>Telephone number is too short.</font><br>")
            err = 1

    return err


def derive_poss_hrs(fields):
    possHrs = []
    estimTime = int(fields['estim_time'])
    if (fields['time_window'] == 'any'):
        start, stop = 8, 20
    else:
        interval = fields['time_window'].split("-")
        start = int(interval[0])
        stop = int(interval[1])
        print("\nTime Window = " + str(start) + "-" + str(stop) + ", estim time = " + str(estimTime) + "\n")

    for i in range(start, stop-estimTime):
        possHrs.append(i)

    return possHrs

def derive_poss_intervals(fields):
    possIntervals = '[' #[]
    estimTime = int(fields['estim_time'])
    if (fields['time_window'] == 'any'):
        start, stop = 8, 20
    else:
        interval = fields['time_window'].split("-")
        start = int(interval[0])
        stop = int(interval[1])
        print("\nTime Window = " + str(start) + "-" + str(stop) + ", estim time = " + str(estimTime) + "\n")

    first = True
    for i in range(start, stop-estimTime):
        if first == False: 
            intrv = ","
        else: 
            intrv = ""
            first = False
        intrv += "'" + str(i)+"-"+str(i+estimTime) + "'"
        #print("<br>intrv = " + str(intrv) + "<br>")
        possIntervals += intrv #.append(intrv)

    possIntervals += "]"
    return possIntervals



main()
