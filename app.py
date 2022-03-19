from flask import Flask, render_template, request
from googletrans import Translator, constants
import re
import requests
from bs4 import BeautifulSoup
import lxml
import sqlite3





#from googleapiclient.discovery import build

app = Flask(__name__)

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():

    translator = Translator()
    #get user input
    usrinp = request.form.get("input")
    #selected language
    lang_sel = request.form.get("lang")

    #translate and combine query with url
    destlang = translator.translate(usrinp, dest=lang_sel)
    url = ('https://www.google.com/search?q='+ destlang.text)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    #url = url.replace(" ", "%")

    r = requests.get(url, headers)

#    riposta = (soup.select("a[href^='/url?q']"))
    
    htmlfile = BeautifulSoup(r.text, 'lxml')
    htmlfile = htmlfile.find("div", { "id" : "main" })
    htmlfile = htmlfile.select("a[href^='/url?q']")
    with open('templates/output.htm', 'w') as f:
        f.write(str(htmlfile))

    with open('templates/output.htm', 'r') as f:
        htmlfile = f.read()
        #htmlfile = htmlfile.replace("/url?q=", "")
        
    with open('templates/output.htm', 'w') as f:
        f.write(str(htmlfile))

    links = BeautifulSoup(htmlfile, 'lxml')   
    url = links.find_all(href=True)

    desc = links.text

    #print(type(desc))
    #print(desc)
    
    connection = sqlite3.connect('res.db')
    cursor = connection.cursor()

    mk_table = """CREATE TABLE IF NOT EXISTS
    res(req_id INTEGER PRIMARY KEY, url TEXT, desc TEXT)"""

    cursor.execute(mk_table)
    cursor.execute("INSERT INTO res(req_id, url, desc) VALUES (?, ?, ?)", [destlang, url, desc])

    link = cursor.execute("SELECT * FROM res WHERE req_id = ?", destlang)

    #riposta = (htmlfile.select("a[href^='/url?q']"))
    
       

### google API search method...
### WORKS BUT NEEDS OUTPUT REFINED
##    api_key = "AIzaSyAov-Ip81hFJ-OUyAz_TglOXSNdJB8lJpQ"
##    cse_key = "bd886c913f1c54e46"  
##
##    resource = build("customsearch", 'v1', developerKey=api_key).cse()
##    result = resource.list(q=req, cx=cse_key).execute()

#   WRITE TO FILE
#    with open('templates/output.txt', 'w') as f:
#        f.write(str(riposta))
#
#    with open('templates/output.txt', 'r') as f:
#        strip = f.read()
#        strip = strip.replace("[", "")
#        strip = strip.replace("<body>", "")
#        strip = strip.replace("<head>", "")
#        strip = strip.replace("<html>", "")
#        strip = strip.replace("</body>", "")
#        strip = strip.replace("</head>", "")
#        strip = strip.replace("</html>", "")
#        strip = strip.replace("]", "")
#        strip = strip.replace(",", "")
#        strip = strip.replace("img", "empty")
#        strip = strip.replace("<div", "<br")
#        strip = strip.replace("</div", "<br")
#        strip = strip.replace("/url?q=", "")
#
#    with open('templates/output.txt', 'w') as f:
#        f.write(str(soup))
#        
    return render_template("result.html", translation = destlang.text, url = link)

