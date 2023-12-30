from app import Admin, app, db

with app.app_context():
    db.create_all()
    admin = Admin(user_email="admin@zoo.com")
    db.session.add(admin)
    db.session.commit()
