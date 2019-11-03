from flask import render_template, redirect, url_for, flash, Markup, jsonify, request
from flask_login import LoginManager, current_user, login_required, logout_user, login_user
import subprocess
from flask_restplus import Resource

from app import app, db, models
from app.forms import LoginForm, RegisterForm, SpellChecker

import os

basedir = os.path.abspath(os.path.dirname(__file__))
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.session_protection = "strong"


@login_manager.user_loader
def user_loader(user_id):
    return models.LoginUser.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('spell_checker'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.LoginUser.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(Markup(
                'Invalid username or password <li class="meir" id="result"> incorrect Username/password or Two-factor failure </li>'))
            print("INVALID")
            return redirect(url_for('login'))
        login_user(user)
        flash(Markup('Logged in successfully. <li class="meir" id="result"> success </li>'))
        return redirect(url_for('spell_checker'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = models.LoginUser(username=form.username.data, mfa=form.mfa.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(Markup('Congratulations, you are now a registered user! <li class="meir" id="success"> success </li>'))
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    else:
        flash(Markup('Something went wrong. Please try to register again <li class="meir" id="success"> failure </li>'))
        return render_template('register.html', title='Sign Up', form=form)


@app.route('/spell_check', methods=['GET', 'POST'])
def spell_checker():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = SpellChecker()
    if form.validate_on_submit():
        f = open("words.txt", "w")
        f.write(form.command.data)
        f.close()

        user = models.LoginUser.query.filter_by(username=current_user.get_id()).first()
        user.set_spell_query(form.command.data)


        p2 = subprocess.Popen(basedir + '/a.out words.txt wordlist.txt', stdin=None, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        p3 = p2.stdout
        output = None
        for words in p3:
            words = words.decode("utf-8").strip().split()
            for word in words:
                if output is None:
                    output = word
                else:
                    output = output + ", " + word

        if output is None:
            output = " No misspelled words"

        user.set_spell_result(output)
        db.session.commit()

        flash(
            Markup('<li id=textout>Misspelled words are:  </li><li class="meir" id="misspelled"> ' + output + ' </li>'))

    return render_template('spell_check.html', title="Spell Check App", form=form)


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
def history():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        data = current_user.get_spell_query()
        try:
            data = data.split(',')
        except AttributeError:
            return render_template('history.html', title="User History", data=False)
        return render_template('history.html', title="User History", data=data)


@app.route('/history/<queryid>')
def history_q(queryid=None):
    if not current_user.is_authenticated or queryid is None:
        return redirect(url_for('history'))
    else:
        try:
            int_queryid = int(queryid[5:])
        except:
            print(int_queryid)
            print("Bad User input")
           # return redirect(url_for('history'))
        data = current_user.get_spell_query()
        result = current_user.get_spell_result()
        print(data)
        print(result)
        data = data.split(',')[int_queryid - 1]
        result = result.split(',')[int_queryid - 1]
        print(data)
        return render_template('queryid.html', title="Query ID " + str(int_queryid), data=data, result=result, queryid=str(int_queryid))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('index')
