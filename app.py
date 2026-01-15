import os
from flask import Flask, render_template, request, jsonify
from models import db, Income, Expense
from datetime import datetime

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-12345'

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/income', methods=['POST'])
def add_income():
    try:
        data = request.json
        if not data or 'amount' not in data or 'month' not in data or 'year' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if record exists for month/year, update or create
        income = Income.query.filter_by(month=int(data['month']), year=int(data['year'])).first()
        if income:
            income.amount = float(data['amount'])
        else:
            income = Income(
                amount=float(data['amount']), 
                month=int(data['month']), 
                year=int(data['year'])
            )
            db.session.add(income)
        
        db.session.commit()
        return jsonify({"message": "Income saved successfully", "amount": income.amount})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/expense', methods=['POST'])
def add_expense():
    try:
        data = request.json
        required = ['category', 'amount', 'date']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400

        date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        new_expense = Expense(
            category=data['category'],
            amount=float(data['amount']),
            date=date_obj.date(),
            description=data.get('description', ''),
            month=date_obj.month,
            year=date_obj.year
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({"message": "Expense added successfully", "expense": new_expense.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/<int:year>/<int:month>', methods=['GET'])
def get_expenses(year, month):
    expenses = Expense.query.filter_by(year=year, month=month).order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])

@app.route('/api/summary/<int:year>/<int:month>')
def get_summary(year, month):
    try:
        income_record = Income.query.filter_by(year=year, month=month).first()
        salary = income_record.amount if income_record else 0
        
        expenses = Expense.query.filter_by(year=year, month=month).all()
        total_spent = sum(e.amount for e in expenses)
        
        # Category breakdown
        categories = {}
        for e in expenses:
            categories[e.category] = categories.get(e.category, 0) + e.amount
            
        return jsonify({
            "income": salary,
            "total_expenses": total_spent,
            "balance": salary- total_spent,
            "percentage": (total_spent / salary * 100) if salary > 0 else 0,
            "category_data": categories
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    try:
        expense = Expense.query.get_or_404(id)
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Expense deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
