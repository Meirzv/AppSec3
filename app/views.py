from flask import render_template, redirect, url_for, flash, Markup
from flask_login import LoginManager, current_user, login_required, logout_user, login_user
import subprocess
from datetime import datetime

from app import app, db, models
from app.forms import LoginForm, RegisterForm, SpellChecker, HistoryAdmin, name, LoginHistoryAdmin

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
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time)
        current_user.set_logs_in(current_time)
        current_user.set_logs_out('N/A.')
        db.session.commit()
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


@app.route('/history', methods=['GET', 'POST'])
def history():
    global name
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif current_user.is_admin():
        form = HistoryAdmin()
        if form.validate_on_submit():
            user = models.LoginUser.query.filter_by(username=form.username.data).first()
            if user is None:
                form.username.data = "'" + form.username.data + "'" + " Not a Valid User"
                return render_template('history.html', title="User History", data=False, form=form)
            name = form.username.data
            data = user.get_spell_query()
            try:
                data = data.split('{cut}')
            except AttributeError:
                return render_template('history.html', title="User History", data=False, form=form)
            return render_template('history.html', title="User History", data=data, form=form)
        else:
            data = current_user.get_spell_query()
            form.username.data = current_user.get_id()
            try:
                data = data.split('{cut}')
            except AttributeError:
                return render_template('history.html', title="User History", data=False, form=form)
            return render_template('history.html', title="User History", data=data, form=form)

    else:
        data = current_user.get_spell_query()
        try:
            data = data.split('{cut}')
        except AttributeError:
            return render_template('history.html', title="User History", data=False)
        return render_template('history.html', title="User History", data=data)


@app.route('/history/<queryid>')
def history_q(queryid=None):
    global name
    if not current_user.is_authenticated or queryid is None:
        return redirect(url_for('history'))
    else:
        try:
            int_queryid = int(queryid[5:])
        except:
            print(int_queryid)
            print("Bad User input")
            return redirect(url_for('history'))
        if current_user.is_admin():
            if name is None:
                name = current_user.get_id()

            user = models.LoginUser.query.filter_by(username=name).first()
            data = user.get_spell_query()
            result = user.get_spell_result()

        else:
            name = current_user.get_id()
            data = current_user.get_spell_query()
            result = current_user.get_spell_result()
        data = data.split('{cut}')[int_queryid - 1]
        result = result.split('{cut}')[int_queryid - 1]
        return render_template('queryid.html', title="Query ID " + str(int_queryid), data=data, result=result,
                               queryid=str(int_queryid), name=name)


@app.route("/logout")
@login_required
def logout():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    current_user.del_last_logout_value()
    current_user.set_logs_out(current_time)
    db.session.commit()
    logout_user()
    return redirect('index')

@app.route("/login_history", methods=['GET', 'POST'])
def loginHistory():
    if current_user.is_authenticated and current_user.is_admin():
        form = LoginHistoryAdmin()
        if form.validate_on_submit():
            user = models.LoginUser.query.filter_by(username=form.username.data).first()
            try:
                logs_in = user.get_logs_in().split('{cut}')
                logs_out = user.get_logs_out().split('{cut}')
            except: #NoneType
                return render_template('LoginHistoryAdmin.html', title="No Logs to Show", form=form, flag=False)
            print(logs_in)
            print(logs_out)
            return render_template('LoginHistoryAdmin.html', title="Login History", name=form.username.data,
                                   logs_in=logs_in, logs_out=logs_out, flag=True, form=form)
        else:
            return render_template('LoginHistoryAdmin.html', title="Login History", form=form, flag=False)
    else:
        return redirect('index')

