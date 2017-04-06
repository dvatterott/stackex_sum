from flask import request, redirect, Markup, render_template, url_for
from Web_App import app
from random import randint
import requests
import markdown
import random
from bs4 import BeautifulSoup

from Web_App.StackExchange_Query import *

# --------- create object for querying stackoverflow --------- #
se_query = setup_se_api_requests()
so = se_query.stack_exchange_query()

# --------- get sentences predictions --------- #
find_sent = helpful_sentences()

highlight_css = """
    .highlightme { background-color:#FFFF00; }
    """
warning_text = """
        I'm only a python expert, so my helpfulness here is questionable. :/ \n
    """
nogood_text = """
        I didn't find any helpful answers here. :T \n
    """
highlight_start = '<span class="highlightme">'
highlight_end = '</span>'


def fix_line_spacing(text, name):
    if len(text) == 0:
        text = [name]
    elif len(text) == 1:
        text = [text]
    else:
        for i, item in enumerate(text):
            text[i] = Markup(item)
    return text


def fix_links(soup, tag_type, find_str, stack_url='http://stackoverflow.com'):
    if find_str == 'form':
        call_dict = {'action': True}
    else:
        call_dict = {'href': True}

    for tag in soup.findAll(find_str, call_dict):
        if tag[tag_type].startswith('/'):
            if tag[tag_type].startswith('//'):
                continue
            tag[tag_type] = stack_url + tag[tag_type]

    return soup


def add_text(soup, input_txt):
    body = soup.body
    body.insert(0, soup.new_tag('h1'))
    body.insert(0, soup.new_tag('br'))
    body.insert(0, soup.new_tag('br'))
    body.insert(0, soup.new_tag('br'))
    new_tag = soup.new_tag('span')
    new_tag['class'] = 'highlightme'
    body.insert(0, new_tag)
    body.h1.insert(0, input_txt)
    return body


@app.route('/')
def answers_input():

    f = open('./Web_App/siftingtheoverflowpost_long.md', 'r')
    md = f.read()

    return render_template("input.html", md=Markup(markdown.markdown(md)))


@app.route('/output')
def receive_input_query_se():
    url = request.args.get("url")
    q_id = [int(s) for s in url.split('/') if s.isdigit()]
    if len(q_id) == 0:
        q_id = [39378902]
    StackObj = acquire_SE_info(so, q_id)
    StackObj.model_prep = False  # prep for rnn instead of bow
    StackObj.sentences = True
    StackObj.get_question_Info()
    StackObj.get_answer_Info()

    good_sent = find_sent.find_helpful_sentences(StackObj)
    good_answers = good_sent['good_sent_text']

    num_good_answers = len(good_answers)

    r = requests.get(StackObj.url)
    html_text = r.text

    soup = BeautifulSoup(html_text, "lxml")
    head = soup.head
    head.insert(1, soup.new_tag('style', type='text/css'))
    head.style.append(highlight_css)
    soup.head = head

    soup = StackObj.highlight_good_answers(soup, good_answers)

    soup = fix_links(soup, 'action', 'form')
    soup = fix_links(soup, 'href', 'link')
    soup = fix_links(soup, 'href', 'a')

    if 'python' not in StackObj.tags:
        soup.body = add_text(soup, warning_text)

    if num_good_answers == 0:
        soup.body = add_text(soup, nogood_text)

    return render_template("output.html",
                           text=Markup(soup))


@app.route('/slides')
def slides():
    return render_template("slides.html")
