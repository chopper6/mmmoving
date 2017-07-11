#!/usr/bin/python
import cgi
print('Content-Type: text/html\n\n')

def main():
    form = cgi.FieldStorage()
    print(form)
    title = cgi.getFirst('title')
    print(title)

main()
