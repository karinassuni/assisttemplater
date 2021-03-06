import os
import urllib.request

from assistscraper import articulation_url, articulation_text_from_html

from assisttemplater import create_vuejs_template, jsonify, tokenize


url = articulation_url('AHC', 'CSUB', 'LBST')
with urllib.request.urlopen(url) as response:
    articulation_page = response.read()

    if not os.path.exists("sample"):
        os.makedirs("sample")

    with open('sample/articulation.html', 'wb') as file:
        file.write(articulation_page)

articulation_text_lines = articulation_text_from_html(articulation_page).split('\n')

articulation_tokens = tokenize(articulation_text_lines)

with open('sample/template.html', 'w') as file:
    file.write(create_vuejs_template(articulation_tokens))

with open('sample/articulation.json', 'w') as file:
    file.write(jsonify(articulation_tokens))
