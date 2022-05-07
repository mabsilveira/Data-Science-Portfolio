
import os
import subprocess
import sys
import locale
import smtplib
from datetime import datetime, date, time, timedelta
from itertools import groupby
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from requests_html import HTML, HTMLSession
from pylatex import Document, Section, Subsection, Command, Package
from pylatex.utils import italic, NoEscape, bold


def fill_document(doc):
    """Add a section, a subsection and some text to the document.
    :param doc: the document
    :type doc: :class:`pylatex.document.Document` instance
    """

    j = 0

    for article_author in article_authors:
        i = 0
        n = article_author[0]

        with doc.create(Section(n)):
            while i < article_author[1]:
                ti = full_article[j][1] + ', ' + full_article[j][3][:-11]
                s = full_article[j][2] + '\n\n'
                te = full_article[j][4]

                with doc.create(Subsection(ti)):
                    doc.append(bold(s))
                    for paragraph in te:
                        paragraph_n = paragraph + '\n\n'
                        doc.append(paragraph_n)

                i += 1
                j += 1


if __name__ == '__main__':

    print(locale.getlocale())
    print(locale.setlocale(locale.LC_ALL, 'pt_PT'))

    """ WEB SCRAPER """

    # list all authors to scrape
    authors = [
        'author_1',
        'author_2',
        'author_3',
        'author_4',
        'author_5',
        'author_n'
    ]

    url = 'https://newspaper.base/url/autor/'

    session = HTMLSession()

    full_article = []

    for author in authors:
        url_author = url + author + '/'

        r = session.get(url_author)

        # get html of list of articles given author articles
        articles = r.html.find('.mod.mod-posttype-opinion .meta')

        for article in articles:
            title = article.find(
                'span:last-child', first=True).attrs['data-title']
            link = article.find('span:last-child',
                                first=True).attrs['data-link']

            # get article html
            r_article = session.get(link)
            article_data = r_article.html.find('article', first=True)

            # get article date
            date = article_data.find(
                '.article-head-meta .article-meta .meta', first=True).text
            date_obj = datetime.strptime(date, '%d %b %Y, %H:%M')
            t = datetime.now()

            # check if article is less than 7 days old
            if t-date_obj > timedelta(days=7):
                break

            # get article data
            name = article_data.find('.columnist-info-name', first=True).text
            synopsis = article_data.find(
                '.article-head-content-headline-lead', first=True).text
            body = article_data.find(
                '.article-body-content', first=True).find('p')
            texto = []
            for par in body:
                texto.append(par.text)

            # delete ads
            texto.pop(0)
            del texto[4]
            del texto[-1]

            full_article.append([name, title, synopsis, date, texto])

    article_authors = [article[0] for article in full_article]

    # group articles by author
    article_authors = [(i, article_authors.count(i))
                       for i, _ in groupby(article_authors)]

    # define 7 day interval
    week = (t-timedelta(days=7)).strftime('%d %b')+' - '+t.strftime('%d %b')

    """ CREATE PDF DOCUMENT """

    geometry_options = {"tmargin": "2cm", "lmargin": "2.5cm",
                        "rmargin": "2.5cm", "bmargin": "2cm"}

    doc = Document(geometry_options=geometry_options)

    doc.preamble.append(NoEscape(r'\usepackage{fontspec}'))
    doc.preamble.append(NoEscape(r'\usepackage{titlesec}'))
    doc.preamble.append(NoEscape(r'\usepackage{setspace}'))
    doc.preamble.append(NoEscape(r'\usepackage[hidelinks]{hyperref}'))

    doc.preamble.append(NoEscape(
        r'\defaultfontfeatures{Mapping = tex - text, Scale = MatchLowercase}'))
    doc.preamble.append(
        NoEscape(r'\setmainfont{Miller Text Roman}[BoldFont={Roboto Bold}]'))
    doc.preamble.append(NoEscape(r'\addfontfeature{LetterSpace=2.0}'))

    doc.append(NoEscape(r'\pretolerance=10000'))

    doc.append(NoEscape(r'\setstretch{1.2}'))

    doc.append(NoEscape(r'\titleformat{\section}'))
    doc.append(
        NoEscape(r'  {\normalfont\fontsize{20}{15}\bfseries}{\thesection}{1em}{}'))
    doc.append(NoEscape(r'\titleformat{\subsection}'))
    doc.append(
        NoEscape(r'  {\normalfont\fontsize{16}{15}\bfseries}{\thesection}{1em}{}'))

    doc.append(NoEscape(r'\fontsize{13}{13pt}\selectfont'))

    doc.preamble.append(Command('title', 'Cronicas'))
    doc.preamble.append(Command('author', week))
    doc.preamble.append(Command('date', ''))
    doc.append(NoEscape(r'\maketitle'))

    doc.append(NoEscape(r'\tableofcontents'))
    doc.append(NoEscape(r'\bigskip'))

    doc.append(NoEscape(r'\setstretch{1.6}'))

    doc.append(NoEscape(r'\titleformat{\section}'))
    doc.append(
        NoEscape(r'  {\normalfont\fontsize{20}{15}\bfseries}{\thesection}{1em}{}'))
    doc.append(NoEscape(r'\titleformat{\subsection}'))
    doc.append(
        NoEscape(r'  {\normalfont\fontsize{16}{15}\bfseries}{\thesection}{1em}{}'))

    doc.append(NoEscape(r'\fontsize{13}{13pt}\selectfont'))

    fill_document(doc)

    doc.generate_tex('cronicas')

    commands = [
        ['lualatex', 'cronicas' + '.tex'],
        ['makeindex', 'cronicas' + '.aux'],
        ['lualatex', 'cronicas' + '.tex'],
        ['lualatex', 'cronicas' + '.tex']
    ]

    for c in commands:
        subprocess.call(c)

    """ SEND EMAIL """

    email_user = os.environ.get('USER_EMAIL')
    email_password = os.environ.get('USER_PASS')
    email_send = ['marcelodasilveira16@gmail.com']

    t = datetime.now()

    week = (t-timedelta(days=7)).strftime('%d %b')+' - '+t.strftime('%d %b')
    subject = 'Cronicas '+week

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = ', '.join(email_send)
    msg['Subject'] = subject

    body = ''

    for article_author in article_authors:
        if article_author[1] == 1:
            body = body+article_author[0]+': ' + \
                str(article_author[1])+' crónica\n'
        else:
            body = body + article_author[0] + ': ' + \
                str(article_author[1]) + ' crónicas\n'

    msg.attach(MIMEText(body, 'plain'))

    filename = 'cronicas.pdf'
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_password)

    server.sendmail(email_user, email_send, text)
    server.quit()

    # Delete aux files
    os.remove('cronicas.aux')
    os.remove('cronicas.ilg')
    os.remove('cronicas.ind')
    os.remove('cronicas.log')
    os.remove('cronicas.out')
    os.remove('cronicas.tex')
    os.remove('cronicas.toc')
