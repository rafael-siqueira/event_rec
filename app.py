# Main script outputting predictions on HTML table when 'Update events' link is clicked
# Calls run_backend.py, which calls get_data.py first and then prediction.py

import os.path
from flask import Flask
import os
import json
import run_backend
import time

# Creating Flask object
app = Flask(__name__)

def get_predictions():
    events = []
    # Using a file as DB in this first version
    run_backend.update_db()

    with open("new_events.json", 'r') as data_file:
        for line in data_file:
            line_json = json.loads(line)
            events.append(line_json)

    predictions = []
    for event in events:
        predictions.append((event['link'], event['name'], float(event['prediction']), event['platform']))
    # reverse=True: descending order
    predictions = sorted(predictions, key=lambda x: x[2], reverse=True)[:50]
    
    predictions_formatted = []
    for event in predictions:
        predictions_formatted.append("<tr><th><a href=\"{link}\">{name}</a></th><th>{prediction}, {rounded}</th><th>{platform}</th></tr>".format(link=event[0], \
                                        name=event[1], prediction=event[2], rounded=round(event[2]), platform=event[3]))
    return '\n'.join(predictions_formatted)

# Python decorator: what URL will trigger the function below
@app.route('/')
def main_page():
    return """<head><h1>SP Event Recommender</h1></head>
    <body><a href="/update-button/">Update events</a>
    </body>"""

@app.route('/update-button/')
def update_button():
    predictions = get_predictions()
    return """<head><h1>SP Event Recommender</h1></head>
    <table>{}</table>""".format(predictions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')