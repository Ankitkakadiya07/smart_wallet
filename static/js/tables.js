// Table functionality and AJAX operations

let sortState = {};
let currentTable = null;

document.addEventListener('DOMContentLoaded', function () {
  // Initialize table sorting
  initializeTableSorting();

  // Initialize AJAX operations
  initializeAjaxOperations();

  // Initialize table enhancements
  initializeTableEnhancements();

  console.log('Tables JavaScript initialized');
});

function initializeTableSorting() {
  // Enhanced table sorting functionality
  const sortableHeaders = document.querySelectorAll('.sortable');

  sortableHeaders.forEach(function (header) {
    header.addEventListener('click', function () {
      sortTable(this);
    });

    // Add visual indicators
    header.style.cursor = 'pointer';
    header.title = `Click to sort by ${header.textContent.trim()}`;
  });
}

function initializeAjaxOperations() {
  // AJAX operations for dynamic table updates
  setupDeleteHandlers();
  setupRefreshHandlers();
  setupPaginationHandlers();

  console.log('AJAX operations initialized');
}

function initializeTableEnhancements() {
  // Add row hover effects and animations
  const tables = document.querySelectorAll('table');

  tables.forEach(table => {
    currentTable = table;

    // Add row hover effects
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      row.addEventListener('mouseenter', function () {
        this.style.transform = 'scale(1.01)';
      });

      row.addEventListener('mouseleave', function () {
        this.style.transform = 'scale(1)';
      });
    });

    // Add loading overlay capability
    addLoadingOverlay(table);
  });
}

function sortTable(header) {
  const table = header.closest('table');
  const tbody = table.querySelector('tbody');
  const sortKey = header.dataset.sort || header.textContent.trim().toLowerCase();
  const columnIndex = Array.from(header.parentElement.children).indexOf(header);

  // Determine sort direction
  const currentDirection = sortState[sortKey] || 'asc';
  const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
  sortState[sortKey] = newDirection;

  // Update header visual indicators
  updateSortHeaders(table, header, newDirection);

  // Get all rows and sort them
  const rows = Array.from(tbody.querySelectorAll('tr'));

  rows.sort((a, b) => {
    const aCell = a.cells[columnIndex];
    const bCell = b.cells[columnIndex];

    let aValue = getCellValue(aCell, sortKey);
    let bValue = getCellValue(bCell, sortKey);

    // Handle different data types
    if (sortKey === 'date') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    } else if (sortKey === 'amount') {
      aValue = parseFloat(aValue.replace(/[^0-9.-]/g, '')) || 0;
      bValue = parseFloat(bValue.replace(/[^0-9.-]/g, '')) || 0;
    } else {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    let comparison = 0;
    if (aValue > bValue) comparison = 1;
    if (aValue < bValue) comparison = -1;

    return newDirection === 'desc' ? -comparison : comparison;
  });

  // Show loading state
  showTableLoading(table);

  // Re-append sorted rows with animation
  setTimeout(() => {
    rows.forEach((row, index) => {
      row.style.animation = 'none';
      tbody.appendChild(row);

      // Stagger animations
      setTimeout(() => {
        row.style.animation = `fadeInUp 0.3s ease-out ${index * 0.05}s both`;
      }, 10);
    });

    hideTableLoading(table);
  }, 200);

  console.log(`Table sorted by ${sortKey} (${newDirection})`);
}

function getCellValue(cell, sortKey) {
  // Extract value based on sort key
  switch (sortKey) {
    case 'date':
      const dateElement = cell.querySelector('.fw-bold');
      return dateElement ? dateElement.textContent.trim() : cell.textContent.trim();

    case 'amount':
      const amountElement = cell.querySelector('.amount-cell, .text-success, .text-danger');
      return amountElement ? amountElement.textContent.trim() : cell.textContent.trim();

    case 'category':
      const categoryElement = cell.querySelector('.badge, .category-badge');
      return categoryElement ? categoryElement.textContent.trim() : cell.textContent.trim();

    case 'source':
    case 'title':
      const titleElement = cell.querySelector('.fw-bold');
      return titleElement ? titleElement.textContent.trim() : cell.textContent.trim();

    default:
      return cell.textContent.trim();
  }
}

function updateSortHeaders(table, activeHeader, direction) {
  // Remove sort classes from all headers
  const headers = table.querySelectorAll('th.sortable');
  headers.forEach(header => {
    header.classList.remove('sort-asc', 'sort-desc');
  });

  // Add sort class to active header
  activeHeader.classList.add(`sort-${direction}`);
}

function setupDeleteHandlers() {
  // Enhanced delete functionality with AJAX
  document.addEventListener('click', function (e) {
    const deleteBtn = e.target.closest('.btn-outline-danger, .delete-btn');
    if (!deleteBtn) return;

    const href = deleteBtn.getAttribute('href');
    if (!href || !href.includes('/delete/')) return;

    e.preventDefault();

    const row = deleteBtn.closest('tr');
    const itemType = href.includes('/income/') ? 'income' : 'expense';
    const itemId = href.match(/\/(\d+)\/delete\//)?.[1];

    if (confirm(`Are you sure you want to delete this ${itemType} transaction?`)) {
      deleteRowAjax(row, itemType, itemId, href);
    }
  });
}

function setupRefreshHandlers() {
  // Setup refresh button handlers
  document.addEventListener('click', function (e) {
    const refreshBtn = e.target.closest('#refresh-table, .refresh-btn');
    if (!refreshBtn) return;

    e.preventDefault();

    const table = refreshBtn.closest('.card').querySelector('table');
    if (table) {
      refreshTable(table.id || 'main-table');
    }
  });
}

function setupPaginationHandlers() {
  // Setup pagination handlers (if pagination is implemented)
  document.addEventListener('click', function (e) {
    const paginationLink = e.target.closest('.pagination a');
    if (!paginationLink) return;

    e.preventDefault();

    const url = paginationLink.getAttribute('href');
    if (url) {
      loadTablePage(url);
    }
  });
}

function deleteRowAjax(row, itemType, itemId, fallbackUrl) {
  // Show loading state on row
  row.style.opacity = '0.5';
  row.style.pointerEvents = 'none';

  // AJAX delete request
  fetch(`/api/${itemType}/${itemId}/delete/`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
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
      // Animate row removal
      row.style.animation = 'fadeOutUp 0.3s ease-out';

      setTimeout(() => {
        row.remove();
        updateTableStats();
        showSuccessMessage(`${itemType} transaction deleted successfully!`);
      }, 300);

      console.log(`${itemType} deleted:`, data);
    })
    .catch(error => {
      console.error('Error deleting item:', error);

      // Restore row state
      row.style.opacity = '';
      row.style.pointerEvents = '';

      // Fallback to regular page navigation
      if (confirm('AJAX delete failed. Redirect to delete page?')) {
        window.location.href = fallbackUrl;
      } else {
        showErrorMessage(`Failed to delete ${itemType}. Please try again.`);
      }
    });
}

function refreshTable(tableId) {
  const table = document.getElementById(tableId) || currentTable;
  if (!table) {
    console.warn('Table not found for refresh');
    return;
  }

  showTableLoading(table);

  // Determine API endpoint based on current page
  let endpoint = '/api/transactions/';
  if (window.location.pathname.includes('/income/')) {
    endpoint = '/api/income/';
  } else if (window.location.pathname.includes('/expense/')) {
    endpoint = '/api/expenses/';
  }

  fetch(endpoint, {
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
      updateTableContent(table, data.transactions || data);
      updateTableStats(data.stats);
      showSuccessMessage('Table refreshed successfully!');
    })
    .catch(error => {
      console.error('Error refreshing table:', error);
      showErrorMessage('Failed to refresh table data.');
    })
    .finally(() => {
      hideTableLoading(table);
    });
}

function updateTableContent(table, transactions) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;

  // Clear existing content
  tbody.innerHTML = '';

  if (!transactions.length) {
    // Show empty state
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = `
      <td colspan="100%" class="text-center text-muted py-4">
        <i class="fas fa-inbox fa-3x mb-3 d-block"></i>
        <h5>No transactions found</h5>
      </td>
    `;
    tbody.appendChild(emptyRow);
    return;
  }

  // Add transaction rows
  transactions.forEach((transaction, index) => {
    const row = createTableRow(transaction);
    row.style.animationDelay = `${index * 0.05}s`;
    tbody.appendChild(row);
  });
}

function createTableRow(transaction) {
  const row = document.createElement('tr');
  row.className = 'fade-in';
  row.dataset.id = transaction.id;

  // This would need to be customized based on the specific table structure
  // For now, return a basic row structure
  row.innerHTML = `
    <td>${formatDate(transaction.date)}</td>
    <td>${transaction.title || transaction.source}</td>
    <td>${formatCurrency(transaction.amount)}</td>
    <td>
      <div class="btn-group btn-group-sm">
        <a href="/income/${transaction.id}/edit/" class="btn btn-outline-primary btn-sm">
          <i class="fas fa-edit"></i>
        </a>
        <a href="/income/${transaction.id}/delete/" class="btn btn-outline-danger btn-sm">
          <i class="fas fa-trash"></i>
        </a>
      </div>
    </td>
  `;

  return row;
}

function updateTableStats(stats) {
  if (!stats) return;

  // Update statistics cards if they exist
  const totalElement = document.querySelector('#total-income, #total-expenses');
  if (totalElement && stats.total) {
    totalElement.textContent = formatCurrency(stats.total);
  }

  const countElement = document.querySelector('.stats-card h4');
  if (countElement && stats.count) {
    countElement.textContent = stats.count;
  }
}

function showTableLoading(table) {
  const overlay = table.querySelector('.loading-overlay');
  if (overlay) {
    overlay.style.display = 'flex';
  }
}

function hideTableLoading(table) {
  const overlay = table.querySelector('.loading-overlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

function addLoadingOverlay(table) {
  const overlay = document.createElement('div');
  overlay.className = 'loading-overlay';
  overlay.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 10;
  `;
  overlay.innerHTML = '<i class="fas fa-spinner fa-spin fa-2x text-primary"></i>';

  const container = table.closest('.table-responsive') || table.parentElement;
  container.style.position = 'relative';
  container.appendChild(overlay);
}

function loadTablePage(url) {
  // Load a specific page of table data
  showTableLoading(currentTable);

  fetch(url, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then(response => response.text())
    .then(html => {
      // Update table content with new page
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newTable = doc.querySelector('table');

      if (newTable && currentTable) {
        currentTable.innerHTML = newTable.innerHTML;
        initializeTableEnhancements();
      }
    })
    .catch(error => {
      console.error('Error loading table page:', error);
      showErrorMessage('Failed to load page.');
    })
    .finally(() => {
      hideTableLoading(currentTable);
    });
}

// Utility functions
function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
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

  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 5000);
}

// Export functions for use in other scripts
window.tableUtils = {
  refreshTable,
  sortTable,
  deleteRowAjax,
  formatCurrency,
  formatDate,
  showTableLoading,
  hideTableLoading
};