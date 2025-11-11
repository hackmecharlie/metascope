from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extract_metadata(file_path):
    exif_cmd = ['exiftool', '-json', file_path]

    try:
        result = subprocess.run(exif_cmd, capture_output=True, text=True, check=True)
        metadata_json = result.stdout
        
        metadata = json.loads(metadata_json)[0]
        metadata['SHA256'] = calculate_hash(file_path)
        return metadata
    
    except subprocess.CalledProcessError as e:
        return None


def calculate_hash(filea_path, algorithm='sha256'):
    hash_func = getattr(hashlib, algorithm, None)
    if hash_func:
        hasher = hash_func()
        with open(filea_path, 'rb') as file:
            while chunk := file.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    return None


def compare_metadata(metadata_list):
    parameters = sorted(set().union(*(metadata.keys() for metadata in metadata_list)) - {'SourceFile'})
    diff_indices = {i: [] for i in range(len(metadata_list))}

    for idx, metadata in enumerate(metadata_list):
        for parameter in parameters:
            if all(metadata.get(parameter) == metadata_list[i].get(parameter) for i in range(len(metadata_list))):
                continue
            else:
                diff_indices[idx].append(parameter)

    return diff_indices


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_and_compare', methods=['POST'])
def upload_and_compare():
    file_paths = request.files.getlist('files')
    
    if len(file_paths) >= 2:
        metadata_list = []
        paths_to_display = []

        for file in file_paths:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            metadata = extract_metadata(filename)
            if metadata:
                metadata['Path'] = filename
                metadata_list.append(metadata)
                paths_to_display.append(filename)
            else:
                return jsonify({"error": "Failed to retrieve metadata"})

        diff_indices = compare_metadata(metadata_list)
        return jsonify({"metadata": metadata_list, "paths": paths_to_display, "diff_indices": diff_indices})
    else:
        return jsonify({"error": "Please select at least 2 files for comparison."})


if __name__ == "__main__":
    app.run(debug=True)
