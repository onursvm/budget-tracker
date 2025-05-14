from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        flash('Başarıyla giriş yapıldı!', 'success')
        
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('unit.dashboard'))
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    flash('Başarıyla çıkış yapıldı.', 'success')
    return redirect(url_for('auth.login'))