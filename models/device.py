from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False, unique=True)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Unknown")

    def __repr__(self):
        return f"<Device {self.name}>"