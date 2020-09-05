from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
#from face_util import compare_faces, face_rec, find_facial_features, find_face_locations
import re
import pdb

app = Flask(__name__)

UPLOAD_FOLDER = 'received_files'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#############face_util################
import face_recognition as fr

def compare_faces(file1, file2):
    """
    Compare two images and return True / False for matching.
    """
    # Load the jpg files into numpy arrays
    image1 = fr.load_image_file(file1)
    image2 = fr.load_image_file(file2)
    
    # Get the face encodings for each face in each image file
    # Assume there is only 1 face in each image, so get 1st face of an image.
    image1_encoding = fr.face_encodings(image1)[0]
    image2_encoding = fr.face_encodings(image2)[0]
    
    # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
    results = fr.compare_faces([image1_encoding], image2_encoding)    
    return results[0]

# Each face is tuple of (Name,sample image)    
known_faces = [('Obama','static/obama.jpg'),
               ('Kalyan Mohanty','static/kalyan.jpg'),
               ('Priyanka Pattnaik','static/priyanka.png'),
               ('Barsa Pattnaik','static/barsa.jpg'),
               ('Jaya D Singham','static/jaya.png'),
               ('khirod Behera','static/khirod.png'),
               ('Manas R Mohanty','static/manas.png'),
               ('Priti Sahoo','static/priti.png'),
               ('Smruti S Das','static/smruti.png'),
               ('Susantini Behara','static/susantini.png'),
               ('Prof. Patra','static/principal.jpg')
              ]
    
def face_rec(file):
    """
    Return name for a known face, otherwise return 'Uknown'.
    """
    for name, known_file in known_faces:
        if compare_faces(known_file,file):
            return name
    return 'Unknown' 
    
def find_facial_features(file):
    # Load the jpg file into a numpy array
    image = fr.load_image_file(file)

    # Find all facial features in all the faces in the image
    face_landmarks_list = fr.face_landmarks(image)
    
    # return facial features if there is only 1 face in the image
    if len(face_landmarks_list) != 1:
        return {}
    else:
        return face_landmarks_list[0]
        
def find_face_locations(file):
    # Load the jpg file into a numpy array
    image = fr.load_image_file(file)

    # Find all face locations for the faces in the image
    face_locations = fr.face_locations(image)
    
    # return facial features if there is only 1 face in the image
    if len(face_locations) != 1:
        return []
    else:
        return face_locations[0]        
##############end###############



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/face_match', methods=['POST', 'GET'])
def face_match():
    if request.method == 'POST':
        # check if the post request has the file part
        if ('file1' not in request.files) or ('file2' not in request.files):
            print('No file part')
            return redirect(request.url)

        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        # if user does not select file, browser also submit an empty part without filename
        if file1.filename == '' or file2.filename == '':
            print('No selected file')
            return redirect(request.url)

        if allowed_file(file1.filename) and allowed_file(file2.filename):
            #file1.save( os.path.join(UPLOAD_FOLDER, secure_filename(file1.filename)) )
            #file2.save( os.path.join(UPLOAD_FOLDER, secure_filename(file2.filename)) )
            ret = compare_faces(file1, file2)
            resp_data = {"match": bool(ret)} # convert numpy._bool of ret to bool for json.dumps
            return json.dumps(resp_data)

    # Return a demo page for GET request
    return '''
    <!doctype html>
    <title>Face Match</title>
    <h1>Upload two images</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file1>
      <input type=file name=file2>
      <input type=submit value=Upload>
    </form>
    '''

def print_request(request):
    # Print request url
    print(request.url)
    # print relative headers
    print('content-type: "%s"' % request.headers.get('content-type'))
    print('content-length: %s' % request.headers.get('content-length'))
    # print body content
    body_bytes=request.get_data()
    # replace image raw data with string '<image raw data>'
    body_sub_image_data=re.sub(b'(\r\n\r\n)(.*?)(\r\n--)',br'\1<image raw data>\3', body_bytes,flags=re.DOTALL)
    print(body_sub_image_data.decode('utf-8'))

@app.route('/face_rec', methods=['POST', 'GET'])
def face_recognition():
    if request.method == 'POST':
        # Print request url, headers and content
        print_request(request)

        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files.get('file')
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if allowed_file(file.filename):
            name = face_rec(file)
            resp_data = {'name': name }

            # get parameters from url if any.
            # facial_features parameter:
            param_features = request.args.get('facial_features', '')
            if param_features.lower() == 'true':
                facial_features = find_facial_features(file)
                # append facial_features to resp_data
                resp_data.update({'facial_features': facial_features})

            # face_locations parameter:
            param_locations = request.args.get('face_locations', '')
            if param_locations.lower() == 'true':
                face_locations = find_face_locations(file)
                resp_data.update({'face_locations': face_locations})

            return json.dumps(resp_data)

    return '''
    <!doctype html>
    <title>Face Recognition</title>
    <h1>Upload an image</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/')
def hello_world():
    return 'Face Recognition API'

# Run in HTTP
# When debug = True, code is reloaded on the fly while saved
if __name__=='__main__':
    app.run(debug=True)

# Run in HTTPS
# https://werkzeug.palletsprojects.com/en/0.15.x/serving/#quickstart
# ssl_context_ = ('ssl_keys/key.crt', 'ssl_keys/key.key')
# app.run(host='127.0.0.1', port='5000', ssl_context=ssl_context_)
# output: Running on https://127.0.0.1:5001/
