from django.shortcuts import render
# from django.http import HttpResponse

# from django.views.generic import View

import re

from bs4 import BeautifulSoup as bs
import requests
from django.shortcuts import redirect


sess = None

def request_on_site(login, password):
    global sess
    # Auth and create Session

    login_page = 'https://dl.cdu.edu.ua/login/index.php'

    sess = requests.Session()
    sess.post(login_page, data={'username': login, 'password': password})

    return sess


def main_page_parse(sess):
    # BeautifulSoup func

    main_page = 'https://dl.cdu.edu.ua/my/'

    req = sess.get(main_page)

    soup = bs(req.text, 'lxml')

    return soup


def parse_of_course(soup):
    # Parse of My courses

    course_list = []

    i = 0

    courses = soup.find_all('div', class_='hidden-xs-down visible-phone')

    for course in courses:

        course_body = course.find('div', class_='media-body')
        h4 = course_body.find('h4', class_='h5')
        name_of_course = h4.find('a').text
        link_of_course = h4.find('a').get('href')

        if None:
            continue
        else:
            course_list.append([i, name_of_course, link_of_course])
        i += 1

    return course_list


class CourseData:


    def __init__(self, url):

        # Initialization of args

        self.sess = sess
        self.url = url



    def page_parse(self):
        # BeautifulSoup func

        req = self.sess.get(self.url)

        soup = bs(req.text, 'lxml')

        return soup


    def course_parse(self):
        # Parse course data

        course_inside = []

        ul = self.page_parse().find('ul', class_='topics')
        li_list = ul.find_all('li', role='region')
        for li in li_list:
            if li.get('id') != 'section-0':
                section = []
                content = li.find('div', class_='content')
                section_title = content.find('h3', class_='sectionname').text
                content_ul = content.find('ul', class_='section img-text')

                content_li = content_ul.find_all('li', class_='activity')
                section.append(section_title)
                for li_c in content_li:
                    try:
                        li_title = li_c.find('span', class_='instancename').text
                        li_link = li_c.find('a').get('href')

                        mod = re.search(r"\/mod\/(\w+)", li_link).group(1)
                        if mod == "page":
                            li_link = Definer(li_link).page_parser()
                        elif mod == "url":
                            body = sess.get(li_link).text
                            soup = bs(body, 'lxml')
                            div = soup.find('div', class_='urlworkaround')
                            if div in soup:
                                li_link = div.find('a').get('href')
                            else:
                                redirect = sess.get(li_link)
                                li_link = redirect.url
                        # elif mod == "resource":
                        #     load = sess.get(li_link)
                        #     file_name = re.search(r"\w+.pdf", li_link).group(0)
                        #     with open(file_name, "wb") as code:
                        #         code.write(load.content)
                        section.append([li_title, li_link])
                    except:Exception
                course_inside.append(section)


            else:
                continue

        return course_inside


class Definer:

    def __init__(self, link):
        self.link = link
        self.sess = sess

    def soup_of_link(self):
        req = self.sess.get(self.link).text
        soup = bs(req, 'lxml')

        return soup

    def page_parser(self):
        soup = self.soup_of_link()
        i_frame_link = soup.find('iframe', frameborder=0).get('src')

        return i_frame_link




def post(request):
    login = request.POST.get('login', False)
    password = request.POST.get('password', False)
    course_list = parse_of_course(main_page_parse(request_on_site(login, password)))

    return render(request, 'my_page/my_page.html', context={'course_list': course_list})


def get(request):
    global sess
    global course_data
    id_course = re.search('\d+', str(request.path)).group(0)
    course_list = parse_of_course(main_page_parse(sess))
    course_url = course_list[int(id_course)][2]
    course_data = CourseData(course_url).course_parse()
    course_name = course_list[int(id_course)][1]

    return render(request, 'my_page/course_data.html', context={'course_name': course_name, 'course_inside': course_data})


# def link_maker(request):
#     global course_data
#
#     for item in course_data:
#         if item[1] == 'page':
#             return redirect(Definer(item[2]).page_parser())