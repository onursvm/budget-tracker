from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    units = User.query.filter_by(role='unit').all()
    return render_template('admin/dashboard.html', units=units)

@bp.route('/register_unit', methods=['GET', 'POST'])
@login_required
@admin_required
def register_unit():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten alınmış!', 'error')
        else:
            new_unit = User(username=username, role='unit')
            new_unit.password = password
            db.session.add(new_unit)
            db.session.commit()
            flash('Yeni harcama birimi başarıyla oluşturuldu!', 'success')
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/register_unit.html')

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin' and user.id == current_user.id:
        flash('Kendi admin hesabınızı silemezsiniz!', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Kullanıcı başarıyla silindi!', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Şifreler eşleşmiyor!', 'error')
        else:
            user.password = new_password
            db.session.commit()
            flash('Şifre başarıyla sıfırlandı!', 'success')
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/reset_password.html', user=user)

@bp.route('/change_admin_password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_admin_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Mevcut şifre yanlış!', 'error')
        elif new_password != confirm_password:
            flash('Yeni şifreler eşleşmiyor!', 'error')
        else:
            current_user.password = new_password
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi!', 'success')
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/change_admin_password.html')