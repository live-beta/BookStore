from flask import Flask, render_template

@app.route('/index')
def index():
	return render_template('templates/index.html')