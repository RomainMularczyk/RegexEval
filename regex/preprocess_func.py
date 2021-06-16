import re

def remove_widespace(text):
    regex = re.compile("\s+")
    text = re.sub(regex, " ", text)
    return text

def remove_n(text):
    regex = re.compile(" nn.")
    text = re.sub(regex, "", text)
    return text

def remove_crlf(text):
    regex = re.compile("\n|\r")
    text = re.sub(regex, " ", text)
    return text