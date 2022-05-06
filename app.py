from flask import Flask, render_template, request, redirect
from googletrans import Translator, constants
import re, requests, lxml
from bs4 import BeautifulSoup
import sqlite3 as sql
import json

app = Flask(__name__)

@app.route("/")
@app.route("/immer")
def immer():
    con = sql.connect('immer.db')
    con.row_factory = sql.Row  
    cur = con.cursor()
    langs = con.execute('SELECT * FROM langs ORDER BY language ASC')

    return render_template("immer.html", langs = langs)

@app.route("/recent")
def recent():

    con = sql.connect('immer.db')
    con.row_factory = sql.Row  
    cur = con.cursor()
    recents = con.execute('SELECT DISTINCT string, * FROM qlog ORDER BY id DESC LIMIT 100;')
    langs = con.execute('SELECT * FROM langs ORDER BY language ASC')      
    return render_template("recent.html", recents = recents, langs = langs)

@app.route("/result", methods=["POST"])
def result():
    #translator is feeling empy inside and waiting for someone to talk to it.
    translator = Translator()
    #get user input
    usrinp = request.form.get("input")
    #selected language
    lang_sel = request.form.get("lang")
    #ip logging
    ipinfo = request.form.get("ipinfo")

    # create url to qry geolocation site...
    response = requests.get('https://geolocation-db.com/jsonp/' + ipinfo)
    result = response.content.decode()
    result = result.split("(")[1].strip(")")
    result  = json.loads(result)
    country = result['country_name']
    country_code = result['country_code']
    city = result['city']

    #translate and combine query with url
    destlang = translator.translate(usrinp, dest=lang_sel)

    #combine url with user input.
        #possible that this could be exchanged for other search engines.
        # setting number of results to 30
        # adding safe filter to query
    url = ('https://www.google.com/search?hl=' + lang_sel + '&q=' + destlang.text + '&num=30' + '&safe=active')


    con = sql.connect('immer.db')
    con.row_factory = sql.Row  
    cur = con.cursor()
    langs = con.execute('SELECT * FROM langs ORDER BY language ASC')
    con.execute('INSERT INTO qlog (url, string, trans, country, country_code, city, target_lang) VALUES (?, ?, ?, ?, ?, ?, ?)', (url, usrinp, destlang.text, country, country_code, city, lang_sel))
    con.commit()

    #user agent to assure google that it's not the end of the world
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    #combine variables generated by user input
    r = requests.get(url, headers)

    #parse the data and do the first round of cleaning annd saving values. Rinse, repeat.
        #review later for ways to clean code and maybe abstract it. 
    htmlfile = BeautifulSoup(r.text, 'lxml')
    htmlfile = htmlfile.find("div", { "id" : "main" })
    htmlfile = htmlfile.select("a[href^='/url?q']")
    with open('output.htm', 'w', encoding='utf-8') as f:
        f.write(str(htmlfile))
    with open('output.htm', 'r', encoding='utf-8') as f:
        htmlfile = f.read()
        htmlfile = htmlfile.replace("/url?q=", "https://www.google.com/url?q=")
    with open('output.htm', 'w', encoding='utf-8') as f:
        f.write(str(htmlfile))
    links = BeautifulSoup(htmlfile, 'lxml')   
    url = links.find_all(href=True)
    with open('output.htm', 'r', encoding='utf-8') as f:
        soup = f.read()

    #reformatting and removing unwanted tags
    invalid_tags = ['div', 'html', 'body', 'p', 'h3', 'span']
    links = BeautifulSoup(soup, 'lxml')
    for tag in invalid_tags: 
        for match in links.findAll(tag):
            match.replaceWithChildren()

    #replace commas with div brackets to break up the container.
    links = re.sub(">, ", "></p></td></tr><tr><td><p>", str(links))

    # consider using list to deal with broken images
    #attr_tags = ['src=', 'style=', 'id=', 'class=']
    links = re.sub('src=', 'ignore=', str(links))
    links = re.sub('style=', 'ignore=', str(links))
    links = re.sub('id=', 'ignore=', str(links))

    #use of empty italics tag to nullify unwanted image data and preserve the alt attrbt as the anchore text
    links = re.sub('" class=', '<i ignore=', str(links))
    links = re.sub('></a>', '></i></a>', str(links))
    links = re.sub('<img alt="', '', str(links))

    #modify anchor to open in new tab
    links = re.sub("<a ", "<i class='bi bi-link-45deg'></i><a id='emmir' target='_blank' ", str(links))

    #modify google links
    googleref = translator.translate('Results from Google', lang_sel)
    aboutimmer = translator.translate('Learn about iMMEr', lang_sel)
    resources = translator.translate('language learning resources', lang_sel)

    links = re.sub("Learn more", "</a><a href='https://www.google.com/search?q=best+language+learning+apps'>" + str(resources.text), str(links))
    links = re.sub("Sign in", "</a><a href='https://github.com/iamgillespie/immersearch.git'>" + str(aboutimmer.text), str(links))
    links = re.sub("Preferences", "</a><a href='https://www.google.com/'>" + str(googleref.text) +"</a>", str(links))

    #strip brackets
    links = (links.strip('[').strip(']'))
           
    return render_template("result.html", translation = destlang.text, links = links, ipinfo = ipinfo, langs = langs)