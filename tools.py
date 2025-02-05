import json
import os
from flask import current_app

def load_json_data(filename):
    json_path = os.path.join(current_app.root_path, 'static', 'data', filename)
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)
