import requests
from bs4 import BeautifulSoup
import smtplib
import time
import json


class Course:
    def __init__(self, *, crn, name, status):
        self.crn = crn
        self.name = name
        self.status = status


def extract_courses_from_web(*, termcode: str, course_names: [str], crns: [int] = []) -> [Course]:
    url = 'https://banssb.fhda.edu/PROD/fhda_opencourses.P_GetCourseList'

    payload = {'termcode': termcode}

    # sending post request and saving response as response object
    r = requests.request('post', url=url, data=payload)

    # extracting response text
    # print(r.text)

    soup = BeautifulSoup(r.content, 'html.parser')

    courses = []

    for course_name_tag in soup.find_all('td', text=True):
        if type(course_name_tag.find_previous_sibling()) != type(None):
            crn = course_name_tag.find_previous_sibling().string
            if course_name_tag.text in course_names or crn in crns:
                name = course_name_tag.string
                status = course_name_tag.find_next_sibling().string

                course = Course(name=name, crn=crn, status=status)

                courses.append(course)

    return courses


def send_mail(*, message, address, password):
    TO = address
    SUBJECT = '--COURSE UPDATE ALERT--'

    # Gmail Sign In
    gmail_sender = address
    gmail_passwd = password

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', message])
    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('email sent')
    except:
        print('error sending mail')

    server.quit()


def main():
    with open('config.json', 'r') as fp:
        config = json.load(fp)

    while True:
        print(time.strftime('%H:%M:%S', time.localtime()))
        for course in extract_courses_from_web(termcode=config['termcode'], course_names=config['courses'], crns=config['crns']):
            print(course.name, ' ', course.crn, ': ', course.status)
            if course.status == 'Waitlist':
                send_mail(message=course.name + ' is now ' + course.status + '. CRN: ' + course.crn,
                          address=config['email'],
                          password=config['password'])
                time.sleep(1200)
        time.sleep(180)


if __name__ == '__main__':
    main()
