from app import Flask, flash, app, render_template, request, redirect, url_for, os, allowed_file
from werkzeug.utils import secure_filename
from models import Simulation

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():

	if request.method == 'POST':
		file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if Simulation(filename).process_all_habitat_simulations():
            	return redirect('/static/output/sample_output.txt')

	return redirect(url_for('home_page'))