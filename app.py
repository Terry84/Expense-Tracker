import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-12345')

# Supabase configuration
SUPABASE_URL = os.environ.get("https://myoeqwawrxojqnorkuhm.supabase.co")
SUPABASE_KEY = os.environ.get("sb_publishable_NGsv28fRCpfBj4Ib1L1ZIA_vAAaLWPs")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/income', methods=['POST'])
def add_income():
    try:
        data = request.json
        if not data or 'amount' not in data or 'month' not in data or 'year' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        month, year = int(data['month']), int(data['year'])
        amount = float(data['amount'])

        # Check if record exists
        existing = supabase.table('income').select('*').eq('month', month).eq('year', year).execute()

        if existing.data:
            # Update existing
            id = existing.data[0]['id']
            response = supabase.table('income').update({"amount": amount}).eq('id', id).execute()
        else:
            # Create new
            response = supabase.table('income').insert({
                "amount": amount,
                "month": month,
                "year": year
            }).execute()
        
        return jsonify({"message": "Income saved successfully", "amount": amount})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expense', methods=['POST'])
def add_expense():
    try:
        data = request.json
        required = ['category', 'amount', 'date']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400

        date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        
        new_expense = {
            "category": data['category'],
            "amount": float(data['amount']),
            "date": data['date'],
            "description": data.get('description', ''),
            "month": date_obj.month,
            "year": date_obj.year
        }
        
        response = supabase.table('expenses').insert(new_expense).execute()
        return jsonify({"message": "Expense added successfully", "expense": response.data[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/<int:year>/<int:month>', methods=['GET'])
def get_expenses(year, month):
    try:
        response = supabase.table('expenses') \
            .select('*') \
            .eq('year', year) \
            .eq('month', month) \
            .order('date', desc=True) \
            .execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary/<int:year>/<int:month>')
def get_summary(year, month):
    try:
        # Get Income
        income_res = supabase.table('income').select('amount').eq('year', year).eq('month', month).execute()
        salary = income_res.data[0]['amount'] if income_res.data else 0
        
        # Get Expenses
        expense_res = supabase.table('expenses').select('category', 'amount').eq('year', year).eq('month', month).execute()
        expenses = expense_res.data
        
        total_spent = sum(e['amount'] for e in expenses)
        
        # Category breakdown
        categories = {}
        for e in expenses:
            cat = e['category']
            categories[cat] = categories.get(cat, 0) + e['amount']
            
        return jsonify({
            "income": salary,
            "total_expenses": total_spent,
            "balance": salary - total_spent,
            "percentage": (total_spent / salary * 100) if salary > 0 else 0,
            "category_data": categories
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    try:
        supabase.table('expenses').delete().eq('id', id).execute()
        return jsonify({"message": "Expense deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)