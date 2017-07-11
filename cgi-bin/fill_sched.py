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

    sched = None
    j=0
    for row in db.execute('SELECT job_schedule, worker_schedule FROM schedule WHERE date = ' + str(date)):
        sched = row
        j+=1
    if (j > 1): print("<font color=red><b><br>Error multiple schedules found for given day.<br></b></font>")

    if not sched:
        jobs = [] 
        hours = [None for i in range(8,21)] # again ASSUMES 8-8 work days, same as range(0,13) i think
        for row in db.execute('SELECT  id, poss_intervals FROM active_jobs WHERE date = ' + str(date)):
            jobs.append(row)

        num_scheds = 1
        scheds = scheduler.build_multiple(jobs,hours,num_scheds)
        sched = scheds[0]
    
    single_sched_table(sched, db)
    print('<br><br><br>')
    print('<div id="sched_holder">Helooooo</div>')
    table_buttons()


def table_buttons():
    print('<br><br>')
    generic_button('modify','Modify')
    generic_button('shuffle','Shuffle')
    generic_button('save','Save')
    print('''<script>
$( "#save" ).click(function() {
   $.ajax({
    url: "/~choppe1/cgi-bin/save_sched.py",
    data: {
        title : $("#sched_holder").attr('id')
    }
}).success(function(data, status, xhr) {
    if (data)
        alert(data);
});

});
    </script>''')


def single_sched_table(sched, db):
    print('''
        <table border="0" cellspacing="50" align="center" style="font-size:1.25em;">
        <p class="sansserif">
        <tr>''')

    #for ele in db.execute('PRAGMA table_info(active_jobs)'):
    #    print('<th>' + str(ele[1]) + '</th>')
    print('<th>Hour</th> <th>Block Hour</th> <th>Worker</th> <th>Client Name <br>(click for details)</th> <th>Set Start Hour</th> <th>Set Worker</th> <th>Finish Job</th> <th>Cancel Job</th></tr>')
    print("<br><br><br>")

    num_slots = 13
    workers = ['worker1','worker2', 'worker3'] #temp

    client_names, poss_intervals = [None for i in range(num_slots)], [None for i in range(num_slots)]
    details = [[] for i in range(num_slots)]
    detail_titles = ['from_address', 'to_address', 'phone', 'email', 'num_ppl', 'num_rooms', 'num_stairs', 'elevator', 'comments'] #way to automate?

    if (sched):
        for i in range(num_slots):
            if (sched[i] or sched[i]==0):
                for row in db.execute('SELECT client_name, poss_intervals, from_address, to_address, phone, email, num_ppl, num_rooms, num_stairs, elevator FROM active_jobs WHERE id = ' + str(sched[i])):
                    client_names[i] = row[0]
                    poss_intervals[i] = scheduler.str_intervals_to_list(row[1])
                    details[i] = row[2:]
            #else: client_names[i] = ' '

    start_hour = 8
    for i in range(len(client_names)):
        print('<tr><td>' + str(i+start_hour) + '</td> <td> ')
        generic_dropdown('blockWorkers_'+str(i), workers)
        full = True
        if (i>0): 
            if (client_names[i] == client_names[i-1]): full = False
        if (client_names[i] != None and full==True):
            print('</td> <td> [Worker] </td> <td>')
            collapsible(client_names[i], details[i], detail_titles) 
            print('</td> <td>')
            set_hr_choices(poss_intervals[i], i, 'set_hr')
            print('</td> <td>')
            generic_dropdown('setWorkers_' + str(i), workers)
            print('</td> <td>')
            generic_button('finish_'+str(i), 'Finish')
            print('</td> <td>')
            generic_button('finish_'+str(i), 'Cancel')
            print('</td>')
        elif (client_names[i] != None):
            print('</td> <td> [Worker] </td> <td>')
            print(str(client_names[i]) + '</td> <td></td><td></td><td></td><td></td>')
        else: 
            print('</td><td></td><td></td><td></td><td></td><td></td><td></td> ')
        print('</tr>')
    print('</table>')
    collapsible_js()


def set_hr_choices(poss_intervals, row, col):
    print('<select id=' + str(row) + "_" + str(col) + '>')
    print('<option value=none> </option>')
    for intrv in poss_intervals: 
        start, stop = intrv.split("-")
        print('<option value=' + start + '>' + start + '</option>')
    print('</select>')


def generic_dropdown(idd, vals):
    print('<select id=' + str(idd) + '>')
    print('<option value=none> </option>')
    for val in vals:
        print('<option value=' + str(val) + '>' + str(val) + '</option>')
    print('</select>') 

def generic_button(idd, text):
    print('<button type=button id=' + str(idd) + '>' + str(text) + '</button>')

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
