from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Income(db.Model):
    __tablename__ = 'income'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "month": self.month,
            "year": self.year
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # Rent, Food, etc.
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "amount": self.amount,
            "date": self.date.strftime('%Y-%m-%d'),
            "description": self.description,
            "month": self.month,
            "year": self.year
        }
