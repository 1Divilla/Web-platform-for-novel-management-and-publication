from flask import Flask, Response, render_template, redirect, url_for, request, flash, session
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

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Intentar encontrar el usuario por el correo
        user = User.query.filter_by(email=email).first()

        if user:
            # Verificar si la contraseña coincide (sin encriptación)
            if user.password == password:
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
    # Buscar la imagen del usuario en la base de datos
    user = User.query.get(user_id)
    if user and user.image:
        return Response(user.image, mimetype='image/png')  # Asegúrate de usar el tipo de mimetype correcto
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        print("Tablas creadas:", inspector.get_table_names())

    app.run(debug=True)
