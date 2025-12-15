// Dashboard JavaScript functionality
// Chart.js integration for income vs expense visualization

let financialChart = null;
let currentChartType = 'pie';
let refreshInterval = null;

document.addEventListener('DOMContentLoaded', function () {
  // Initialize dashboard charts when DOM is loaded
  initializeCharts();

  // Set up event listeners for interactive elements
  setupEventListeners();

  // Initialize auto-refresh (optional)
  setupAutoRefresh();

  console.log('Dashboard JavaScript initialized');
});

function initializeCharts() {
  // Get chart canvas element
  const ctx = document.getElementById('financialChart');
  if (!ctx) {
    console.warn('Chart canvas not found');
    return;
  }

  // Initialize Chart.js visualization
  initializeFinancialChart();
  console.log('Dashboard charts initialized');
}

function setupEventListeners() {
  // Chart type toggle buttons
  const pieBtn = document.getElementById('chart-pie');
  const barBtn = document.getElementById('chart-bar');

  if (pieBtn) pieBtn.addEventListener('click', () => switchChartType('pie'));
  if (barBtn) barBtn.addEventListener('click', () => switchChartType('bar'));

  // Refresh button
  const refreshBtn = document.getElementById('refresh-transactions');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', refreshDashboardData);
  }

  // Financial cards click handlers for smooth interactions
  document.querySelectorAll('.financial-card').forEach(card => {
    card.addEventListener('click', function () {
      this.style.transform = 'scale(0.98)';
      setTimeout(() => {
        this.style.transform = '';
      }, 150);
    });
  });
}

function setupAutoRefresh() {
  // Optional auto-refresh functionality
  const autoRefreshEnabled = false; // Can be toggled based on user preference

  if (autoRefreshEnabled) {
    refreshInterval = setInterval(() => {
      refreshDashboardData(true); // Silent refresh
    }, 60000); // Refresh every minute
  }
}

function initializeFinancialChart() {
  const ctx = document.getElementById('financialChart').getContext('2d');

  // Get data from global dashboardData variable (passed from Django template)
  const income = window.dashboardData ? window.dashboardData.totalIncome : 0;
  const expenses = window.dashboardData ? window.dashboardData.totalExpenses : 0;

  // Chart configuration
  const chartConfig = {
    type: currentChartType,
    data: {
      labels: ['Income', 'Expenses'],
      datasets: [{
        label: 'Financial Overview',
        data: [income, expenses],
        backgroundColor: [
          'rgba(17, 153, 142, 0.8)',  // Income color (green)
          'rgba(252, 70, 107, 0.8)'   // Expense color (red)
        ],
        borderColor: [
          'rgba(17, 153, 142, 1)',
          'rgba(252, 70, 107, 1)'
        ],
        borderWidth: 2,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Income vs Expenses Overview',
          font: {
            size: 16,
            weight: 'bold'
          },
          color: '#333'
        },
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const label = context.label || '';
              const value = formatCurrency(context.parsed || context.raw);
              const total = income + expenses;
              const percentage = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      },
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  };

  // Destroy existing chart if it exists
  if (financialChart) {
    financialChart.destroy();
  }

  // Create new chart
  financialChart = new Chart(ctx, chartConfig);
}

function switchChartType(type) {
  currentChartType = type;

  // Update button states
  document.querySelectorAll('.btn-group .btn').forEach(btn => {
    btn.classList.remove('active');
  });
  document.getElementById(`chart-${type}`).classList.add('active');

  // Update chart configuration for different types
  if (type === 'bar') {
    financialChart.config.type = 'bar';
    financialChart.config.options.scales = {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return formatCurrency(value);
          }
        }
      }
    };
  } else {
    financialChart.config.type = 'pie';
    delete financialChart.config.options.scales;
  }

  // Update chart
  financialChart.update('active');
}

function refreshDashboardData(silent = false) {
  console.log('Dashboard data refresh requested');

  const refreshBtn = document.getElementById('refresh-transactions');

  if (!silent && refreshBtn) {
    // Show loading state
    const originalContent = refreshBtn.innerHTML;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    refreshBtn.disabled = true;
  }

  // AJAX request to get updated financial data
  fetch('/api/dashboard-data/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Update dashboard with new data
      updateFinancialSummary(data);
      updateRecentTransactions(data.recent_transactions || []);

      if (!silent) {
        showSuccessMessage('Dashboard refreshed successfully!');
      }

      console.log('Dashboard data updated:', data);
    })
    .catch(error => {
      console.error('Error refreshing dashboard data:', error);

      if (!silent) {
        showErrorMessage('Failed to refresh dashboard data. Please try again.');
      }
    })
    .finally(() => {
      if (!silent && refreshBtn) {
        // Restore button state
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        refreshBtn.disabled = false;
      }
    });
}

function updateRecentTransactions(transactions) {
  const tbody = document.getElementById('transactions-tbody');
  if (!tbody || !transactions.length) return;

  // Clear existing rows
  tbody.innerHTML = '';

  // Add new transaction rows
  transactions.forEach((transaction, index) => {
    const row = createTransactionRow(transaction);
    row.style.animationDelay = `${index * 0.1}s`;
    tbody.appendChild(row);
  });
}

function createTransactionRow(transaction) {
  const row = document.createElement('tr');
  row.className = 'transaction-row fade-in';
  row.dataset.type = transaction.type;
  row.dataset.id = transaction.id;

  const isIncome = transaction.type === 'income';
  const amountClass = isIncome ? 'text-success' : 'text-danger';
  const amountPrefix = isIncome ? '+' : '-';
  const badgeClass = isIncome ? 'bg-success' : 'bg-danger';
  const iconClass = isIncome ? 'fa-arrow-up' : 'fa-arrow-down';

  row.innerHTML = `
    <td>
      <span class="fw-bold">${formatDate(transaction.date)}</span>
      <br><small class="text-muted">${formatDayOfWeek(transaction.date)}</small>
    </td>
    <td>
      <span class="badge ${badgeClass} rounded-pill">
        <i class="fas ${iconClass} me-1"></i>${transaction.type}
      </span>
    </td>
    <td>
      <div class="fw-bold">${transaction.title}</div>
      <small class="text-muted">${transaction.category || 'General'}</small>
      ${transaction.note ? `<br><small class="text-info">${transaction.note}</small>` : ''}
    </td>
    <td>
      <span class="${amountClass} fw-bold">${amountPrefix}${formatCurrency(transaction.amount)}</span>
    </td>
    <td>
      <div class="btn-group btn-group-sm">
        <button class="btn btn-outline-primary btn-sm" onclick="editTransaction('${transaction.type}', ${transaction.id})" title="Edit">
          <i class="fas fa-edit"></i>
        </button>
        <button class="btn btn-outline-danger btn-sm" onclick="deleteTransaction('${transaction.type}', ${transaction.id})" title="Delete">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </td>
  `;

  return row;
}

function editTransaction(type, id) {
  const url = type === 'income' ? `/income/${id}/edit/` : `/expense/${id}/edit/`;
  window.location.href = url;
}

function deleteTransaction(type, id) {
  if (confirm(`Are you sure you want to delete this ${type} transaction?`)) {
    const url = type === 'income' ? `/income/${id}/delete/` : `/expense/${id}/delete/`;
    window.location.href = url;
  }
}

function showSuccessMessage(message) {
  showMessage(message, 'success');
}

function showErrorMessage(message) {
  showMessage(message, 'danger');
}

function showMessage(message, type) {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
  alertDiv.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;

  document.body.appendChild(alertDiv);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 5000);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function formatDayOfWeek(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { weekday: 'long' });
}

// Utility functions for dashboard
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
}

function updateFinancialSummary(data) {
  // Update financial summary cards with new data
  if (data.totalIncome !== undefined) {
    const incomeElement = document.getElementById('total-income');
    if (incomeElement) {
      incomeElement.textContent = formatCurrency(data.totalIncome);
      animateValue(incomeElement, data.totalIncome);
    }
  }

  if (data.totalExpenses !== undefined) {
    const expensesElement = document.getElementById('total-expenses');
    if (expensesElement) {
      expensesElement.textContent = formatCurrency(data.totalExpenses);
      animateValue(expensesElement, data.totalExpenses);
    }
  }

  if (data.currentBalance !== undefined) {
    const balanceElement = document.getElementById('current-balance');
    if (balanceElement) {
      balanceElement.textContent = formatCurrency(data.currentBalance);

      // Update balance color based on value
      balanceElement.className = balanceElement.className.replace(/text-(success|danger|warning)/g, '');
      if (data.currentBalance > 0) {
        balanceElement.classList.add('text-success');
      } else if (data.currentBalance < 0) {
        balanceElement.classList.add('text-danger');
      } else {
        balanceElement.classList.add('text-warning');
      }

      animateValue(balanceElement, data.currentBalance);
    }
  }

  // Update chart if data changed
  if (financialChart && (data.totalIncome !== undefined || data.totalExpenses !== undefined)) {
    financialChart.data.datasets[0].data = [data.totalIncome || 0, data.totalExpenses || 0];
    financialChart.update('active');
  }

  console.log('Financial summary updated', data);
}

function animateValue(element, targetValue) {
  // Add pulse animation to updated values
  element.classList.add('pulse-animation');

  setTimeout(() => {
    element.classList.remove('pulse-animation');
  }, 2000);
}

// Export functions for use in other scripts
window.dashboardUtils = {
  formatCurrency,
  updateFinancialSummary,
  refreshDashboardData,
  switchChartType
};