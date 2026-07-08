// ============================================
// MA'LUMOTLAR
// ============================================

let transactions = [
    { id: 1, type: 'kirim', amount: 1500000, category: 'Oylik maosh', description: 'Yanvar oyligi', date: '2026-01-15' },
    { id: 2, type: 'kirim', amount: 500000, category: 'Biznes daromad', description: 'Freelance', date: '2026-01-18' },
    { id: 3, type: 'chiqim', amount: 250000, category: 'Oziq-ovqat', description: 'Magnet', date: '2026-01-20' },
    { id: 4, type: 'chiqim', amount: 120000, category: 'Transport', description: 'Taksi', date: '2026-01-21' },
    { id: 5, type: 'kirim', amount: 300000, category: 'Sovgʻa', description: "Tug'ilgan kun", date: '2026-01-22' },
    { id: 6, type: 'chiqim', amount: 50000, category: 'Telefon', description: "Uyali aloqa", date: '2026-01-22' },
    { id: 7, type: 'kirim', amount: 2000000, category: 'Oylik maosh', description: 'Fevral oyligi', date: '2026-02-10' },
    { id: 8, type: 'chiqim', amount: 400000, category: 'Uy-joy', description: "Kvartira to'lovi", date: '2026-02-12' },
];

let currentType = 'kirim';
let chartInstance = null;
let categoryChartInstance = null;

// ============================================
// THEME
// ============================================
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    themeToggle.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
    setTimeout(renderCharts, 100);
});

// ============================================
// STATS
// ============================================
function updateStats() {
    const totalIncome = transactions.filter(t => t.type === 'kirim').reduce((s, t) => s + t.amount, 0);
    const totalExpense = transactions.filter(t => t.type === 'chiqim').reduce((s, t) => s + t.amount, 0);
    const balance = totalIncome - totalExpense;
    const growth = totalIncome > 0 ? ((totalIncome - totalExpense) / totalIncome * 100).toFixed(1) : 0;

    document.getElementById('totalIncome').textContent = formatMoney(totalIncome);
    document.getElementById('totalExpense').textContent = formatMoney(totalExpense);
    document.getElementById('totalBalance').textContent = formatMoney(balance);
    document.getElementById('totalGrowth').textContent = (growth >= 0 ? '+' : '') + growth + '%';
}

// ============================================
// TRANSACTIONS
// ============================================
function renderTransactions() {
    const tbody = document.getElementById('transactionsBody');
    const sorted = [...transactions].sort((a, b) => new Date(b.date) - new Date(a.date));
    const latest = sorted.slice(0, 10);

    tbody.innerHTML = latest.map(t => `
        <tr>
            <td><span class="type-badge ${t.type}">${t.type === 'kirim' ? '💰 Kirim' : '💸 Chiqim'}</span></td>
            <td class="${t.type === 'kirim' ? 'amount-income' : 'amount-expense'}">${formatMoney(t.amount)}</td>
            <td>${t.category}</td>
            <td>${formatDate(t.date)}</td>
        </tr>
    `).join('');
}

function formatMoney(amount) {
    if (amount >= 1000000) return (amount / 1000000).toFixed(1) + 'M so\'m';
    if (amount >= 1000) return (amount / 1000).toFixed(0) + 'K so\'m';
    return amount + ' so\'m';
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('uz-UZ', { day: '2-digit', month: 'short' });
}

// ============================================
// CHARTS
// ============================================
function renderCharts() {
    const isDark = document.body.classList.contains('dark');
    const textColor = isDark ? '#9ca3af' : '#6b7280';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';

    // Main Chart
    const ctx = document.getElementById('mainChart').getContext('2d');
    const grouped = {};
    transactions.forEach(t => {
        if (!grouped[t.date]) grouped[t.date] = { kirim: 0, chiqim: 0 };
        grouped[t.date][t.type] += t.amount;
    });

    const dates = Object.keys(grouped).sort();
    const incomeData = dates.map(d => grouped[d].kirim || 0);
    const expenseData = dates.map(d => grouped[d].chiqim || 0);

    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates.map(d => formatDate(d)),
            datasets: [
                {
                    label: 'Kirim',
                    data: incomeData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16,185,129,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointBackgroundColor: '#10b981',
                },
                {
                    label: 'Chiqim',
                    data: expenseData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointBackgroundColor: '#ef4444',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: textColor,
                        font: { size: 11, weight: '500' },
                        boxWidth: 12,
                        padding: 15,
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, font: { size: 10 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor, font: { size: 10 } }
                }
            }
        }
    });

    // Category Chart
    const catCtx = document.getElementById('categoryChart').getContext('2d');
    const categories = {};
    transactions.forEach(t => {
        if (!categories[t.category]) categories[t.category] = 0;
        categories[t.category] += t.amount;
    });

    const catLabels = Object.keys(categories);
    const catData = Object.values(categories);
    const colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6', '#06b6d4'];

    if (categoryChartInstance) categoryChartInstance.destroy();

    categoryChartInstance = new Chart(catCtx, {
        type: 'doughnut',
        data: {
            labels: catLabels,
            datasets: [{
                data: catData,
                backgroundColor: colors.slice(0, catLabels.length),
                borderWidth: 2,
                borderColor: isDark ? '#1a1a2e' : '#ffffff',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textColor,
                        font: { size: 10, weight: '500' },
                        boxWidth: 10,
                        padding: 10,
                    }
                }
            },
            cutout: '65%',
        }
    });
}

// ============================================
// MODAL
// ============================================

function openModal(type) {
    currentType = type;
    document.getElementById('modalTitle').textContent = type === 'kirim' ? '💰 Kirim qo\'shish' : '💸 Chiqim qo\'shish';
    document.getElementById('transactionModal').classList.add('active');
    document.getElementById('amount').value = '';
    document.getElementById('description').value = '';
    document.getElementById('date').value = new Date().toISOString().split('T')[0];
}

function closeModal() {
    document.getElementById('transactionModal').classList.remove('active');
}

document.getElementById('transactionForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const amount = parseFloat(document.getElementById('amount').value);
    const category = document.getElementById('category').value;
    const description = document.getElementById('description').value;
    const date = document.getElementById('date').value || new Date().toISOString().split('T')[0];

    if (!amount || amount <= 0) {
        alert('❌ Iltimos, to\'g\'ri summa kiriting!');
        return;
    }

    transactions.push({
        id: Date.now(),
        type: currentType,
        amount: amount,
        category: category,
        description: description,
        date: date,
    });

    closeModal();
    updateAll();
    alert('✅ Tranzaksiya qo\'shildi!');
});

// ============================================
// CARD MODAL
// ============================================

function openCardModal() {
    document.getElementById('cardModal').classList.add('active');
}

function closeCardModal() {
    document.getElementById('cardModal').classList.remove('active');
}

document.getElementById('cardForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const name = document.getElementById('cardName').value;
    const number = document.getElementById('cardNumber').value.replace(/\s/g, '');
    const balance = parseFloat(document.getElementById('cardBalance').value);

    if (number.length !== 16 || !/^\d+$/.test(number)) {
        alert('❌ Karta raqami 16 ta raqamdan iborat bo\'lishi kerak!');
        return;
    }

    alert(`✅ Karta qo'shildi!\n🏦 ${name}\n🔢 ${number.slice(0,4)}****${number.slice(-4)}\n💰 ${balance.toLocaleString()} so'm`);
    closeCardModal();
    document.getElementById('cardForm').reset();
});

document.getElementById('cardNumber').addEventListener('input', function() {
    let val = this.value.replace(/\s/g, '');
    if (val.length > 16) val = val.slice(0, 16);
    const formatted = val.match(/.{1,4}/g)?.join(' ') || val;
    this.value = formatted;
});

// ============================================
// REPORT
// ============================================

function generateReport() {
    const totalIncome = transactions.filter(t => t.type === 'kirim').reduce((s, t) => s + t.amount, 0);
    const totalExpense = transactions.filter(t => t.type === 'chiqim').reduce((s, t) => s + t.amount, 0);
    const balance = totalIncome - totalExpense;

    const text = `
📊 HISOBOT - kunlik.tizim
${'='.repeat(40)}

💰 Jami Kirim: ${formatMoney(totalIncome)}
💸 Jami Chiqim: ${formatMoney(totalExpense)}
📈 Balans: ${formatMoney(balance)}

📋 Tranzaksiyalar soni: ${transactions.length}

📅 Sana: ${new Date().toLocaleString('uz-UZ')}
    `;

    navigator.clipboard.writeText(text).then(() => {
        alert('✅ Hisobot nusxalandi!');
    }).catch(() => {
        alert(text);
    });
}

// ============================================
// ADD BUTTON
// ============================================

document.getElementById('addBtn').addEventListener('click', () => {
    openModal('kirim');
});

// ============================================
// UPDATE ALL
// ============================================

function updateAll() {
    updateStats();
    renderTransactions();
    renderCharts();
}

// ============================================
// BOSHLASH
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    updateAll();
    console.log('💰 kunlik.tizim sayti ishga tushdi!');
});