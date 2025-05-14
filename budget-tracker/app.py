from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from routes import auth, admin, unit
import locale

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Veritabanı başlatma
    db.init_app(app)
    
    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Blueprint kayıtları
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(unit.bp)
    
    # Template filtresi ekle
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        except:
            locale.setlocale(locale.LC_ALL, '')
        return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Date format filter
    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        if hasattr(value, 'strftime'):
            return value.strftime('%d.%m.%Y %H:%M')
        return value
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Varsayılan admin kullanıcısı
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', role='admin')
            admin_user.password = 'admin123'  # Üretimde daha güçlü şifre kullanın
            db.session.add(admin_user)
            db.session.commit()
    
    app.run(debug=True)