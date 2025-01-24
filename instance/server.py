from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os

# Flask uygulaması ve yapılandırma
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Veritabanı dosyası
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Ana Sayfa
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

# Giriş Yap
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')

# Kayıt Ol
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists.")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Sohbet Sayfası
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

# Çıkış Yap
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# SocketIO - Mesajlaşma
@socketio.on('send_message')
def handle_message(data):
    username = session.get('username', 'Unknown')
    emit('receive_message', {'username': username, 'message': data['message']}, broadcast=True)

if __name__ == '__main__':
    # Veritabanını oluştur
    with app.app_context():
        db.create_all()

    # Uygulamayı başlat
    socketio.run(app, debug=True)
