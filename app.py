from flask import (
    Flask, 
    request, 
    render_template, 
    redirect, 
    url_for, 
    jsonify
)
import os
from os.path import join, dirname
from pymongo import MongoClient
import requests
from datetime import datetime
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)

# password = 'LCzPylmLh3N7KP9j'
# cxn_string = f'mongodb+srv://raden_616_rizki:{password}@cluster0.gcv3hdx.mongodb.net/?retryWrites=true&w=majority'
# client = MongoClient(cxn_string)

# db = client.dbsparta

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition
        })
    msg = request.args.get('msg')
    return render_template('index.html', words=words, msg=msg)

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = "a04c28b0-6c7b-468f-967d-b3e54dab8cca"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    
    response = requests.get(url)
    definitions = response.json()
    
    if not definitions:
        return redirect(url_for(
            'error',
            msg=f'Could not find the word | {keyword} | ; unknown word'
        ))
        
    if type(definitions[0]) is str:
        suggestions = ", ".join(definitions)
        
        return redirect(url_for(
            'error',
            msg=f'Could not find the word | {keyword} | Did you mean one of these word : ; {suggestions}'
        ))
    
    status = request.args.get('status_give', 'new')
    # print(keyword)
    return render_template(
        'detail.html', 
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    
    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y.%m.%d')
    }
    
    db.words.insert_one(doc)
    
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word} was saved!!!'
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word} was delete'
    })
    
@app.route('/error')
def error():
    msg = request.args.get('msg')
    msg = msg.split(' ; ')
    suggestions = msg[1].split(', ')
    print(suggestions)
    msg = msg[0]
    return render_template('error.html', msg=msg, suggestions=suggestions)

@app.route('/practice')
def practice():
    return render_template('practice.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)