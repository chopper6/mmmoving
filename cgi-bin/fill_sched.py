#!/usr/bin/python
import cgi
print('Content-Type: text/html\n\n')
#print()
import cgi, cgitb
import sqlite3, sys
sys.path.insert(0, '/home/2014/choppe1/public_html/mmmoving/cgi-bin')
import scheduler

cgitb.enable()     # for troubleshooting

def main():
    form = cgi.FieldStorage()
    fields = {}
    for key in form.keys():
        fields[key] = str(form.getvalue(str(key)))
    err = check_form_integrity(fields)
    if (err != 0):
        print("<font color=red><b><br>Error in date selection.<br></b></font>")
        return

    date = derive_date(fields) 
    date = '"' + str(date) + '"' 
    db, db_conn = connect_to_DB()
    jobs = [] 
    hours = [None for i in range(8,21)] # again ASSUMES 8-8 work days, same as range(0,13) i think
    for row in db.execute('SELECT  id, poss_intervals FROM active_jobs WHERE date = ' + str(date)):
        jobs.append(row)

    num_scheds = 3
    scheds = scheduler.build_multiple(jobs,hours,num_scheds)
    for sched in scheds:
        single_sched_table(sched, db)
    print('<br><br><br>')

def single_sched_table(sched, db):
    print('''
        <table border="0" cellspacing="50" align="center" style="font-size:1.25em;">
        <p class="sansserif">
        <tr>''')

    #for ele in db.execute('PRAGMA table_info(active_jobs)'):
    #    print('<th>' + str(ele[1]) + '</th>')
    print('<th>Hour</th><th>Client Name <br>(click for details)</th></tr>')
    print("<br><br><br>")

    client_names = [None for i in range(0,13)]
    details = [[] for i in range(0,13)]
    detail_titles = ['from_address', 'to_address', 'phone', 'email', 'num_ppl', 'num_rooms', 'num_stairs', 'elevator', 'comments'] #way to automate?

    if (sched):
        for i in range(0,13):
            if (sched[i] or sched[i]==0):
                for row in db.execute('SELECT client_name, from_address, to_address, phone, email, num_ppl, num_rooms, num_stairs, elevator FROM active_jobs WHERE id = ' + str(sched[i])):
                    client_names[i] = row[0]
                    details[i] = row[1:]
            #else: client_names[i] = ' '

    start_hour = 8
    for i in range(len(client_names)):
        print('<tr><td>' + str(i+start_hour) + '</td><td>')
        if (client_names[i] != None): collapsible(client_names[i], details[i], detail_titles) 
        else: print(' ')
        print('</td></tr>')
    print('</table>')
    collapsible_js()


def check_form_integrity(fields):
    err = 0
    not_nones = ['month', 'day']

    for title in not_nones:
        if (fields[title] == 'none'):
            print("<font color=red>Error: must pick a value for " + title + ".<br></font>")
            err = 1


    return err

def derive_date(fields):
    day = int(fields['day'])
    if (day < 10): day_str = "0" + str(day)
    else: day_str = str(day)
    year = '2017'
    date = year + "-" + str(fields['month']) + "-" + day_str
    fields['date']=date
    return date


def connect_to_DB ():
    path = '/home/2014/choppe1/public_html/mmmoving.db' #i assume full path nec
    conn = sqlite3.connect(path)
    db = conn.cursor()

    return db, conn

def collapsible (mini, expand_list, titles):
    print('<div class="job_title" id=' + str(mini) + '><a>' + str(mini) + '</a></div>')
    print('<ul class="details" id="details_' + str(mini) + '">')
    for i in range(len(expand_list)):
        if expand_list[i] and expand_list[i] != "none":
            print('<li>' + str(titles[i]) + ": " + str(expand_list[i]) + '</li>')
    print('</ul>') 
    #collapsible_js()
    #collapsible_css()

def collapsible_js():
    print('''<script>
$(document).ready(function(){
    $(".details").hide();
    $(".job_title").click(function(){
        name=$(this).attr('id')
        console.log("details_"+name)
        $("#details_"+name).toggle();
        });
    })
</script>''')



def collapsible_js_old():
    print( '''
<script>
$('[data-toggle]').on('click', function(){
  var id = $(this).data("toggle"),
      $object = $(id),
      className = "open";

  if ($object) {
    if ($object.hasClass(className)) {
      $object.removeClass(className)
      $(this).text("Toggle: show");
    } else {
      $object.addClass(className)
      if ($object.hasClass(className))
      $(this).text("Toggle:);
    }
  }
});
</script>
''')

def collapsible_css():
    print('''<script>#list {
  display: none;
  background:#008B8B;
  color:red;
}

#list.open {
  display: block;
  color:blue;
}''')


main()
