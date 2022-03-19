from googletrans import Translator, constants
from pprint import pprint
import webbrowser

# init the Google API translator
translator = Translator()

#take input
langsel = input("Enter target language... ")
inp = input("what are we searching for?: ")

phrase = [inp]


# translate more than a phrase
translations = translator.translate(phrase, dest=langsel)
for translation in translations:
    query = (f"https://www.youtube.com/search?q={translation.text}")
    print(query)

    webbrowser.open(query)