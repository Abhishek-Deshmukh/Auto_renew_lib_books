from pprint import pprint
from requests import Session
from bs4 import BeautifulSoup
import datetime

# Making a session
sess = Session()

#getting the password from a file in a secret location
passwrd=get_password()

# Authentication parameters for login
authentication = {
    'koha_login_context' : 'opac',
    'userid' : '1811004',
    'password' : passwrd
}

# Loggin in
book_list_page = sess.post('http://10.0.2.254:8001/cgi-bin/koha/opac-user.pl', data = authentication) # we send data instead of params while post

# Making a soup of the html
book_list_page_soup = BeautifulSoup(book_list_page.text,features="lxml")

# taking the table out of the soup and seperating the rows in the variable rows in a the form of a list.
table = book_list_page_soup.find('table')
rows=table.find_all('tr')

# checking row by row
for row in rows:
    if check_need_to_renew(row):
        if check_possibility_to_renew(row):
            renew_link=get_renew_link(row)
            # sending the renew request
            book_list_page = sess.get('http://10.0.2.254:8001'+renew)
        else:
            notify_via_email()
    else:
        continue

# closing the session
sess.close

def notify_via_email():
    pprint('You need to get to the library')

def check_need_to_renew(row):
    #date from 3 days after
    today_minus_3days = datetime.date.today()+datetime.timedelta(days=3)
    # scraping the date from the code and converting it into the python's datetime format
    duedate_td = row.find(class_='date_due')
    if not duedate_td: # for the first row which is not required
        return False
    duedate=duedate_td.span['title']
    duedate=duedate.split('T')[0].split('-')
    duedate=datetime.date(day=int(duedate[2]), month=int(duedate[1]),year=int(duedate[0]))
    # checking for the need
    if duedate < today_minus_3days:
        return True
    return False

def check_possibility_to_renew(row):
# number of times left to renew
    renewal_remaining_str = renew_td.text
    renew_times_left=int(((renewal_remaining_str.split('\n')[2]).split(' ')[0])[1])
    if renew_times_left == 0 : # If cannot renew anymore then god save us
        return False

def get_renew_link(row):
    #Scraping out the renewing link
    renew_td = row.find(class_='renew')
    renew = renew_td.a['href']
    return renew

def get_password():
    with open('Password/password') as password_file:
        passwrd=password_file.read()
    return passwrd
