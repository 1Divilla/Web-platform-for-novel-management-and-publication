from flask import Flask, Response, render_template, redirect, url_for, request, flash, session
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import tools as tls
from models import db, User, UserRead, Novel, Chapter

app = Flask(__name__)
app.secret_key = 'mysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def principal():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/browse')
def browse():
    return render_template('browse.html')

@app.route('/update')
def update():
    return render_template('update.html')

from flask import redirect, url_for
from datetime import datetime, timezone, timedelta

@app.route('/delete_account_request', methods=['POST'])
def delete_account_request():
    user = User.query.get(session.get('user_id'))
    if user:
        user.deletion_date = datetime.now(timezone.utc) + timedelta(days=1)
        db.session.commit()
        flash('Account deletion scheduled for 24 hours from now.', 'warning')
    return redirect(url_for('logout'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if user.password == password:
                if user.deletion_date:
                    user.deletion_date = None
                    db.session.commit()
                    flash('Account deletion canceled.', 'info')

                session['user'] = user.nick
                session['email'] = user.email
                session['user_id'] = user.id
                session['date'] = user.date.strftime('%d %B %Y, %H:%M')
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password. Try again.', 'danger')
        else:
            flash('Email not found. Please sign up.', 'danger')

    return render_template('auth.html')


@app.route('/profile_image/<int:user_id>')
def profile_image(user_id):
    user = User.query.get(user_id)
    if user and user.image:
        return Response(user.image, mimetype='image/png')
    else:
        return 'Image not found', 404


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nickname = request.form.get('nickname')

        # Verificar si las contraseñas coinciden
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('auth'))

        with open('static/icons/default.png', 'rb') as f:
            image_data = f.read()  

        new_user = User(
            nick=nickname,
            email=email,
            password=password,
            image=image_data
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth'))

    return render_template('auth.html')


@app.route('/policy')
def policy():
    policy_data = tls.load_json_data('policy.json')
    return render_template('policy.html', policy=policy_data)

@app.route('/terms')
def terms():
    terms_data = tls.load_json_data('terms.json')
    return render_template('terms.html', terms=terms_data)

def delete_scheduled_accounts():
    now = datetime.now(timezone.utc)
    users_to_delete = User.query.filter(User.deletion_date != None, User.deletion_date <= now).all()

    for user in users_to_delete:
        db.session.delete(user)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        delete_scheduled_accounts()
        inspector = inspect(db.engine)
        print("Tablas creadas:", inspector.get_table_names())
    app.run(debug=True)