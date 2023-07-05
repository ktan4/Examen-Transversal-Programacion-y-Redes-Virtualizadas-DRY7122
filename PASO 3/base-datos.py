from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from passlib.hash import pbkdf2_sha256
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Clave secreta para proteger las sesiones

# Configuración de la base de datos
DB_NAME = 'users.db'


def create_users_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password_hash TEXT NOT NULL)''')
    conn.commit()
    conn.close()


def add_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    password_hash = pbkdf2_sha256.hash(password)
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()


def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return pbkdf2_sha256.verify(password, result[0])
    return False


class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired(), EqualTo('confirm_password', message='Las contraseñas deben coincidir')])
    confirm_password = PasswordField('Confirmar Contraseña')
    submit = SubmitField('Registrarse')


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if validate_user(username, password):
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        add_user(username, password)
        flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('dashboard.html', users=users)


if __name__ == '__main__':
    create_users_table()
    app.run(port=4850)
