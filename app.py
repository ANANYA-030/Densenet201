from fpdf import FPDF
import pymongo
import matplotlib.pyplot as plt
import pandas as pd 
import base64
import numpy as np
import cv2
import smtplib
import pyttsx3 
import concurrent.futures
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from time import sleep
import keras as ks
from flask import Flask, render_template, request,jsonify
import tensorflow.python as tf2
import tensorflow as tf
from keras.models import load_model 

new_model = load_model('densenet201.h5')
app = Flask(__name__)
global new


def typing(text):
    for char in text:
        sleep(0.04)
        sys.stdout.write(char)
        sys.stdout.flush()

def textToSpeech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 220)
    engine.say(text)
    engine.runAndWait()
    del engine

def parallel(text):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_tasks = {executor.submit(
            textToSpeech, text), executor.submit(typing, text)}
        for future in concurrent.futures.as_completed(future_tasks):
            try:
                data = future.result()
            except Exception as e:
                print(e)

def databaseInsert(name, emailId, age, contact, nu):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client['dense201']
    collection = db['dense201']
    dictionary = {"Name": name, "Email-ID": emailId,
                  "Age": age, "Contact": contact, "Prediction": nu}
    collection.insert_one(dictionary)


predictions = ["Benign","Malignant"]
    
    
def predict_image(img_path, model,name, emailId, age, contact):
    # Load and preprocess the image
    img = ks.preprocessing.image.load_img(img_path, target_size=(224, 224))
    img_array = ks.preprocessing.image.img_to_array(img)
    expected_shape = (-1, 224,224,3) 


    if len(img_array.shape) == 3:  # Check if 3D (height, width, channels)
        img_array = np.expand_dims(img_array, axis=0)  # Add a batch dimension for prediction

    flattened_img = img_array.reshape(expected_shape)
    # Perform prediction
    predictions = model.predict(flattened_img)
    class_names = ['Benign','Malignant']
    predicted_class_index = np.argmax(predictions)
    a = class_names[predicted_class_index]
    print(f"\n\n\n\n\n\nPredicted: {a}\n\n\n\n\n\n")
    

    if(a=="Benign"):
        mm =   f"""
                        BREAST CANCER DIAGNOSIS By TEAM 60

     Patient name:{name}
     Age: {age}
     Email id:{emailId}
     Contact no:{contact}

     Diagnosis:
        Breast Cancer Diagnosis image shows signs of {a}.

     Further advice for treatment: 
     1. Keep up with routine check-ups for breast health monitoring.
     2. Embrace a balanced lifestyle with a healthy diet, exercise, and stress management.
     3. Conduct monthly self-exams to detect any changes early.
     4. Stay informed about breast health, including risks, screening methods, and prevention.
     

     a) For further advice the patient can visit the nearest breast tumor hospital.
     b) To contact us visit our Team 60 web app.
     c) Incase this report is lost, contact Team 60

    """
    elif(a=="Malignant"):
        mm =  f"""
                        BREAST CANCER DIAGNOSIS By TEAM 60

     Patient name:{name}
     Age: {age}
     Email id:{emailId}
     Contact no:{contact}

     Diagnosis:
        Breast Cancer Diagnosis image shows signs of {a}.

     Further advice for treatment: 
     1. Collaborate on a tailored treatment plan with your healthcare team.
     2. Seek emotional support from various sources.
     3. Adopt healthy habits to support treatment effectiveness.
     4. Commit to regular follow-up appointments for monitoring and adjustments.

     a) For further advice the patient can visit the nearest breast tumor hospital.
     b) To contact us visit our Team 60 web app.
     c) Incase this report is lost, contact Team 60

        """
    file1 = open("output.txt", "w") 
    file1.writelines(mm)
    file1.close()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    f = open("output.txt", "r")
    for x in f:
        pdf.cell(200, 8, txt=x, ln=.8, align='L')
    print("Done with pdf")
    databaseInsert(name, emailId, age, contact, a)
    pdf.output('report.pdf')
    body = mm
   
    sender = 'xyz@gmail.com'
    password='abcdefghijklmnop' #create app password
    receiver = emailId
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = 'This email has an attacment, a pdf file'
    message.attach(MIMEText(body, 'plain'))
    pdfname = 'report.pdf'
    binary_pdf = open(pdfname, 'rb')
    payload = MIMEBase('application', 'octate-stream', Name=pdfname)
    payload.set_payload((binary_pdf).read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
    message.attach(payload)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender, password)
    text = message.as_string()
    session.sendmail(sender, receiver, text)
    session.quit()
    print('Mail Sent')
  
    parallel(f"Breast Cancer Diagnosis image shows signs of {a}")
    return a


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def predict():
    name = request.form['name']
    emailId = request.form['emailId']
    contact = request.form['contact']
    age = request.form['age']
    print(name, emailId, contact, age)
    imagefile = request.files['imagefile']
    image_path = "images/"+imagefile.filename
    imagefile.save(image_path)
    predict_image(image_path,new_model,name, emailId, age, contact)
    return render_template('index.html')
    
   

if __name__ == '__main__':
    app.run(port=3030, debug=True)