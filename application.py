import os
from datetime import datetime

from flask import Flask, request, session, redirect, url_for, abort, g
from flask import render_template

from models import db, migrate, User, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///satcounter.db'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = os.environ.get('SATCOUNTER_SECRETKEY',
                                b"""\xd9\xa5D\x0b]>\xa9\xfb\xe8\x90\x04\xb6
                                \xd6\x9d6k\xc8SP\xdb\x84\x94T8\xedI\x84\xc3""")

db.init_app(app)
migrate.init_app(app, db)


def get_countdown():  # Override default render function
    delta = datetime(2017, 11, 16) - datetime.now()
    return delta


@app.before_request
def before_request():
    g.countdown = get_countdown()
    if 'username' in session:
        print(User.query.filter_by(username=session['username']).all())
        g.user = User.query.filter_by(username=session['username']).one()
    else:
        g.user = None


@app.route('/')
def index():
    return redirect(url_for('list_comments'))


@app.route('/comments')
def list_comments():
    limit = 5
    page = int(request.args.get('page', 1))
    comments = Message.query.order_by('id').offset((page-1)*limit).limit(limit+1).all()
    is_end = False if len(comments) == 6 else True
    return render_template('comments.html', comments=comments[:5], page=page, end=is_end)


@app.route('/comments/<int:number>')
def get_comment(number: int):
    try:
        comment = Message.query.filter_by(id=number-1).one()
        return render_template('single_comment.html', comment=comment)
    except IndexError:
        abort(404)


# @app.route('/users/')
# def users():
#     return render_template('user_list.html')
#
#
@app.route('/users/<string:username>')
def user_profile(username: str):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    limit = 5
    page = int(request.args.get('page', 1))
    comments = Message.query.filter_by(writer=user).order_by('id')\
                      .offset((page - 1) * limit).limit(limit + 1).all()
    is_end = False if len(comments) == 6 else True
    return render_template('profile.html', comments=comments[:5], page=page, end=is_end)


@app.route('/comments/write', methods=['GET', 'POST'])
def post_comment():
    if g.user is None:
        abort(401)
    if request.method == 'GET':
        return render_template('write.html')
    else:
        msg = Message(g.user, request.form.get('content', ''))
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user is not None and user.valid_password(password):
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credential')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return render_template('register.html', error='User already exists')
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
