from flask import render_template, redirect, url_for, flash, Markup
from flask_login import LoginManager, current_user, login_required, logout_user, login_user
import subprocess
from datetime import datetime

from app import app, db, models
from app.forms import LoginForm, RegisterForm, SpellChecker, HistoryAdmin, LoginHistoryAdmin

import os

from app.models import SpellCheck

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

        #   user = models.LoginUser.query.filter_by(username=current_user.get_id()).first()
        #   user.set_spell_query(form.command.data)

        user_query = models.SpellCheck.query.filter_by(user_id=current_user.get_id()).first()
        # if user_query == None:
        #      query=1
        # else:
        #     query = models.SpellCheck.query.first()
        #     query.query_id = models.SpellCheck.query_id + 1
        #
        #     print(type(query))
        #     print(query.query_id)
        #     print("query id Result=  " + str(query))
        #     db.session.add(user_query)
        # db.session.commit()

        # print("------" + str(user_query) +"------")

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
            output = "No misspelled words"

        # user.set_spell_result(output)

        user_query = models.SpellCheck(spell_query=form.command.data, spell_result=output,
                                       user_id=current_user.get_id())
        db.session.add(user_query)
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
        # Print all users queries
        queries = SpellCheck.query.all()
        queries_dict = dict()
        data = dict()
        for idt in queries:
            queries_dict[idt.query_id] = [idt.spell_result, idt.spell_query, idt.user_id]
        form = HistoryAdmin()
        if form.validate_on_submit():
            user = models.SpellCheck.query.filter_by(user_id=form.username.data).all()
            index = list()
            try:
                for idt in user:
                    data[idt.query_id] = [idt.spell_result, idt.spell_query, idt.user_id]
                    index.append(idt.query_id)
            except:
                form.username.data = "'" + form.username.data + "'" + " Not a Valid User"
                return render_template('history.html', title="User History", data=False, form=form)
            print(index)
            return render_template('history.html', title="User History", data=data, form=form, queries_dict=queries_dict
                                   ,index=index)
        else:
            return render_template('history.html', title="User History", data=False, queries_dict=queries_dict,
                                   form=form)

    else:
        user = models.SpellCheck.query.filter_by(user_id=current_user.get_id()).all()
        data = dict()
        index = list()
        try:
            for idt in user:
                data[idt.query_id] = [idt.query_id, idt.spell_result, idt.spell_query, idt.user_id]
                index.append(idt.query_id)
        except AttributeError:
            return render_template('history.html', title="User History", data=False)
        print(index)
        return render_template('history.html', title="User History", data=data, index=index)


@app.route('/history/<queryid>')
def history_q(queryid=None):
    data = dict()
    if not current_user.is_authenticated or queryid is None:
        return redirect(url_for('history'))
    else:
        try:
            int_queryid = int(queryid[5:])
        except:
            print(int_queryid)
            print("Bad User input")
            return redirect(url_for('history'))
        if current_user.get_id() == 'admin' or current_user.get_id() == True:
            print(current_user.get_id())
            queries = SpellCheck.query.all()

            for idt in queries:
                data[idt.query_id] = [idt.spell_result, idt.spell_query, idt.user_id]

            user = data[int_queryid][2]
            query = data[int_queryid][1]
            result = data[int_queryid][0]

            return render_template('queryid.html', title="Query ID " + str(int_queryid), data=query, outcome=result,
                                   queryid=str(int_queryid), name=user)
        else:
            queries = SpellCheck.query.filter_by(user_id=current_user.get_id()).limit(int_queryid).all()
            n=0
            for idt in queries:
                n = n+1
                data[n] = [idt.spell_result, idt.spell_query, idt.user_id]
            user = data[n][2]
            query = data[n][1]
            result = data[n][0]

            return render_template('queryid.html', title="Query ID " + str(int_queryid), data=query, outcome=result,
                               queryid=str(int_queryid), name=user)


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
            except:  # NoneType
                return render_template('LoginHistoryAdmin.html', title="No Logs to Show", form=form, flag=False)
            print(logs_in)
            print(logs_out)
            return render_template('LoginHistoryAdmin.html', title="Login History", name=form.username.data,
                                   logs_in=logs_in, logs_out=logs_out, flag=True, form=form)
        else:
            return render_template('LoginHistoryAdmin.html', title="Login History", form=form, flag=False)
    else:
        return redirect('index')
