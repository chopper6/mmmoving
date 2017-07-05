#!/usr/bin/python
import random as rd

def build_multiple (jobs, hours, num_build):
    #builds with jobs in diff order
    scheds = []
    for i in range(num_build):
        hours_copy = hours[:]
        scheds.append(build(jobs, hours_copy))
        rd.shuffle(jobs) #some form of reordering
    return scheds



def build (jobs, hours):
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
            if ((hours[i]) != None): 
                free = False
        if (free):
            hours2 = hours
            for i in range(start-hour0,stop-hour0): #CHECK off-by-one err
                hours2[i] = job_id
            if (jobs[1:]): 
                hours = build(jobs[1:], hours2)
                return hours

            else:
                return hours2 

    return False


def str_intervals_to_list(string):
    # assumes ['8-19']-<F12>
    string = string.replace('[','').replace(']','').replace("'",'')
    intrvs = string.split(',')
    return intrvs

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
