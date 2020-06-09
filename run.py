from requests_html import AsyncHTMLSession
import csv
import re  # imports the csv and the regular expression module

asession = AsyncHTMLSession()

urls = ['https://johnmccraess.ocdsb.ca/cms/one.aspx?portalId=233445&pageId=1154152',
'https://johnmccraess.ocdsb.ca/cms/one.aspx?portalId=233445&pageId=1154155', 'https://johnmccraess.ocdsb.ca/cms/one.aspx?portalId=233445&pageId=1154161']


def get_page_function(url: str):

    async def get_page():
        r = await asession.get(url)
        return r

    return get_page

# goes through the html and returns the teacher's name, courses and their site


def process_teacher_courses(teacher_section):
    # split it based on the new line and comma
    name, *courses_filtered = re.split("\n|,",
                                       teacher_section.find("p", first=True).text)

    courses = [course.strip() for course in courses_filtered if course]

    a_link = teacher_section.find("a", first=True)

    site = a_link.attrs.get("href") if a_link else None

    # return a tuple of the name, courses and site
    return (name, courses, site)


results = list(map(lambda url: get_page_function(url), urls))

results_html = asession.run(*results)

classes = {}

for result in results_html:

    response = result.html

    # splitting the thing up, getting rid of the start
    _, *response_td = response.find('td')

    for td in response_td:

        teacher_name, courses, site = process_teacher_courses(td)
        teacher = (teacher_name, site)

        for course in courses:

            course_list = classes.get(course)

            if course_list:
                course_list.append(teacher)
            else:
                classes[course] = [teacher]

    # now that I have all the classes and their teachers, I can write stuff for csv
    csv_file = open("classes.csv", "w")
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(['class', 'teachers', 'websites'])

    for key, value in classes.items():

        names, links = [], []

        for name, link in value:
            names.append(name)
            
            if link:
                links.append(link)

        csv_writer.writerow([key, str(names), str(links)])

    csv_file.close()
