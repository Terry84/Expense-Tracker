let expenseChart = null;

document.addEventListener('DOMContentLoaded', () => {
    // Set default month/year to today
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const yearMonth = `${now.getFullYear()}-${month}`;
    
    const incomeMonthInput = document.getElementById('incomeMonth');
    incomeMonthInput.value = yearMonth;
    
    document.getElementById('expDate').valueAsDate = new Date();

    // Initial load
    updateDashboard();

    // Listeners
    incomeMonthInput.addEventListener('change', updateDashboard);
});

async function saveIncome() { 
    const incomeInput = document.getElementById('incomeInput');
    const monthInput = document.getElementById('incomeMonth');

    if (!incomeInput || !monthInput) {
        console.error("Income or month input not found!");
        return;
    }

    const amount = parseFloat(incomeInput.value);
  
if (isNaN(amount)) {
    alert("Please enter a valid income amount.");
    return;
}

    const dateVal = monthInput.value;

   if (!dateVal) {
    alert("Please select a month.");
    return;
}

    const [year, month] = dateVal.split('-').map(v => parseInt(v, 10));

    try {
        const response = await fetch('/api/income', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, month, year })
        });

        const data = await response.json();
        console.log(data);
        updateDashboard(); // refresh the dashboard after saving
    } catch (err) {
        console.error("Error saving income:", err);
    }
}

async function addExpense() {
    const desc = document.getElementById('expDesc').value;
    const cat = document.getElementById('expCat').value;
    const amt = document.getElementById('expAmt').value;
    const date = document.getElementById('expDate').value;

    if (!amt || !date || !cat) {
        alert("Please fill in category, amount, and date.");
        return;
    }

    try {
        const response = await fetch('/api/expense', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                description: desc,
                category: cat,
                amount: amt,
                date: date
            })
        });
        const result = await response.json();
        if (response.ok) {
            // Reset form
            document.getElementById('expDesc').value = '';
            document.getElementById('expAmt').value = '';
            
            // If the added expense is in the currently viewed month, refresh
            const viewDate = document.getElementById('incomeMonth').value;
            const expenseDatePrefix = date.substring(0, 7); // YYYY-MM
            
            if (viewDate === expenseDatePrefix) {
                updateDashboard();
            }
        } else {
            alert(result.error || "Failed to add expense");
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteExpense(id) {
    if (!confirm("Are you sure you want to delete this expense?")) return;
    
    try {
        const res = await fetch(`/api/expense/${id}`, { method: 'DELETE' });
        if (res.ok) updateDashboard();
    } catch (err) {
        console.error(err);
    }
}

async function updateDashboard() {
    const dateVal = document.getElementById('incomeMonth').value;
    if (!dateVal) return;
    
    const [year, month] = dateVal.split('-');
    const mInt = parseInt(month);
    const yInt = parseInt(year);

    try {
        // Fetch Summary
        const summaryRes = await fetch(`/api/summary/${yInt}/${mInt}`);
        const data = await summaryRes.json();

        // Update Stats
        document.getElementById('dispincome').innerText = `${data.income.toLocaleString()}`;
        document.getElementById('dispSpent').innerText = `${data.total_expenses.toLocaleString()}`;
        document.getElementById('dispBalance').innerText = `${data.balance.toLocaleString()}`;
        document.getElementById('dispPercent').innerText = `${data.percentage.toFixed(2)}%`;

        const spentEl = document.getElementById('dispSpent');
        if (data.total_expenses > data.income && data.income > 0) {
            spentEl.classList.add('text-danger');
        } else {
            spentEl.classList.remove('text-danger');
        }

        // Update Chart
        renderChart(data.category_data);

        // Fetch Detailed List
        const listRes = await fetch(`/api/expenses/${yInt}/${mInt}`);
        const expenses = await listRes.json();
        renderExpenseList(expenses);

    } catch (err) {
        console.error("Error updating dashboard:", err);
    }
}

function renderChart(categoryData) {
    const ctx = document.getElementById('expensePieChart').getContext('2d');
    
    const labels = Object.keys(categoryData);
    const values = Object.values(categoryData);

    if (expenseChart) {
        expenseChart.destroy();
    }

    if (labels.length === 0) {
        // Show empty state if needed, or just clear
        return;
    }

    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', 
                    '#858796', '#5a5c69', '#fd7e14', '#6f42c1', '#e83e8c'
                ],
                hoverBorderColor: "rgba(234, 236, 244, 1)",
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            cutout: '70%'
        }
    });
}

function renderExpenseList(expenses) {
    const tbody = document.getElementById('expenseTableBody');
    tbody.innerHTML = '';

    if (expenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No expenses found for this month</td></tr>';
        return;
    }

    expenses.forEach(exp => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${exp.date}</td>
            <td><span class="badge bg-info text-dark">${exp.category}</span></td>
            <td>${exp.description || '-'}</td>
            <td class="fw-bold">$${exp.amount.toLocaleString()}</td>
            <td>
                <button onclick="deleteExpense(${exp.id})" class="btn btn-sm btn-outline-danger">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}
