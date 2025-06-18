from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import CSRFProtect
from .store import get_all, _save, del_shortcut

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ErnahmBraumeHammerAndSickleCellTransPlantationofCottonandWoolenTexTilesofIndianFoodNetworkingataConventionalLevelUpOnTheWorldWideWeb'

# Wire up CSRF protection
csrf = CSRFProtect(app)

@app.route('/')
def index():
    shortcuts = get_all()
    return render_template('index.html', shortcuts=shortcuts)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    cmd  = request.form['cmd']
    data = get_all()
    data[name] = {"cmd": cmd}
    _save(data)
    return redirect(url_for('index'))

@app.route('/delete/<name>')
def delete(name):
    del_shortcut(name)
    return redirect(url_for('index'))
