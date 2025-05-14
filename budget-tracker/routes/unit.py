from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Budget
from datetime import datetime

bp = Blueprint('unit', __name__, url_prefix='/unit')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'unit':
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.login'))
    
    budgets = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.month.desc()).all()
    return render_template('unit/dashboard.html', budgets=budgets)

@bp.route('/budgets')
@login_required
def budget_list():
    if current_user.role != 'unit':
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.login'))
    
    budgets = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.month.desc()).all()
    return render_template('unit/budget_list.html', budgets=budgets)

@bp.route('/add_budget', methods=['GET', 'POST'])
@login_required
def add_budget():
    if current_user.role != 'unit':
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        month = request.form.get('month')
        total_budget = float(request.form.get('total_budget'))
        spent_22d = float(request.form.get('spent_22d', 0))
        spent_22f = float(request.form.get('spent_22f', 0))
        
        # Aynı ay için kayıt kontrolü
        existing = Budget.query.filter_by(user_id=current_user.id, month=month).first()
        if existing:
            flash('Bu ay için zaten bütçe kaydı bulunmaktadır!', 'error')
            return redirect(url_for('unit.add_budget'))
        
        new_budget = Budget(
            month=month,
            total_budget=total_budget,
            spent_22d=spent_22d,
            spent_22f=spent_22f,
            user_id=current_user.id
        )
        
        db.session.add(new_budget)
        db.session.commit()
        flash('Bütçe bilgileri başarıyla kaydedildi!', 'success')
        return redirect(url_for('unit.dashboard'))
    
    # Varsayılan olarak geçerli ay
    default_month = datetime.now().strftime('%Y-%m')
    return render_template('unit/add_budget.html', default_month=default_month)

@bp.route('/edit_budget/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_budget(id):
    if current_user.role != 'unit':
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.login'))
    
    budget = Budget.query.get_or_404(id)
    
    # Kullanıcı kendisine ait olmayan bütçeyi düzenleyemez
    if budget.user_id != current_user.id:
        flash('Bu bütçe kaydını düzenleme yetkiniz yok!', 'error')
        return redirect(url_for('unit.dashboard'))
    
    if request.method == 'POST':
        budget.total_budget = float(request.form.get('total_budget'))
        budget.spent_22d = float(request.form.get('spent_22d', 0))
        budget.spent_22f = float(request.form.get('spent_22f', 0))
        
        db.session.commit()
        flash('Bütçe bilgileri başarıyla güncellendi!', 'success')
        return redirect(url_for('unit.dashboard'))
    
    return render_template('unit/edit_budget.html', budget=budget)