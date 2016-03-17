#!/usr/bin/env python
#encoding=utf-8
import os
import codecs


PATH = '/data/clawer/html/'
# PATH = '/Users/princetechs5/'
def save_to_html(path, name, html):
    write_type = 'w'
    if not os.path.exists(path):
    	os.makedirs(path)
    new_path = os.path.join(path, name)
    with codecs.open(new_path, write_type, 'utf-8') as f:
        f.write(html)
