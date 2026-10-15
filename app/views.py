from flask import request, render_template
from . import app

@app.route('/')
def main():
    return render_template("resume.html", title="Головна")

@app.route('/homepage')
def home():
    """View for the Home page of website."""
    agent = request.user_agent
    return render_template("homepage.html", agent=agent, title="Домашня сторінка")