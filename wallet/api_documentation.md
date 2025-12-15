# Smart Wallet API Documentation

## Overview

The Smart Wallet API provides RESTful endpoints for managing financial transactions through AJAX operations. All endpoints return JSON responses with consistent status codes and error handling.

## Base URL

All API endpoints are prefixed with `/api/`

## Response Format

All API responses follow this standard format:

```json
{
    "status": "success|error",
    "message": "Optional message",
    "data": {
        // Response data object
    }
}
```

## HTTP Status Codes

- `200 OK` - Successful GET, PUT, DELETE operations
- `201 Created` - Successful POST operations
- `400 Bad Request` - Invalid request data or validation errors
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side errors

## Authentication

Currently, no authentication is required for API endpoints. This may change in future versions.

## Endpoints

### Dashboard Data

#### GET /api/dashboard-data/

Get dashboard summary data including totals and recent transactions.

**Response:**
```json
{
    "status": "success",
    "data": {
        "totalIncome": 5000.00,
        "totalExpenses": 2500.00,
        "currentBalance": 2500.00,
        "recentTransactions": [
            {
                "id": 1,
                "type": "income|expense",
                "title": "Transaction title",
                "category": "Category name",
                "amount": 100.00,
                "date": "2023-12-15",
                "note": "Optional note"
            }
        ]
    }
}
```

### Income Transactions

#### GET /api/income/

Get all income transactions.

**Response:**
```json
{
    "status": "success",
    "data": {
        "transactions": [
            {
                "id": 1,
                "source": "Salary",
                "category": {
                    "id": 1,
                    "name": "Salary"
                },
                "amount": 3000.00,
                "date": "2023-12-15",
                "note": "Monthly salary",
                "created_at": "2023-12-15T10:00:00Z",
                "updated_at": "2023-12-15T10:00:00Z"
            }
        ],
        "stats": {
            "total": 5000.00,
            "count": 5
        }
    }
}
```

#### GET /api/income/{id}/

Get a specific income transaction.

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "source": "Salary",
        "category": {
            "id": 1,
            "name": "Salary"
        },
        "amount": 3000.00,
        "date": "2023-12-15",
        "note": "Monthly salary",
        "created_at": "2023-12-15T10:00:00Z",
        "updated_at": "2023-12-15T10:00:00Z"
    }
}
```

#### POST /api/income/

Create a new income transaction.

**Request Body:**
```json
{
    "category_id": 1,
    "source": "Freelance Work",
    "amount": 500.00,
    "date": "2023-12-15",
    "note": "Optional note"
}
```

**Response (201 Created):**
```json
{
    "status": "success",
    "message": "Income transaction created successfully",
    "data": {
        "id": 2,
        "source": "Freelance Work",
        "category": {
            "id": 1,
            "name": "Freelancing"
        },
        "amount": 500.00,
        "date": "2023-12-15",
        "note": "Optional note",
        "created_at": "2023-12-15T10:00:00Z"
    }
}
```

#### PUT /api/income/{id}/

Update an existing income transaction.

**Request Body (partial updates allowed):**
```json
{
    "source": "Updated source",
    "amount": 600.00,
    "note": "Updated note"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Income transaction updated successfully",
    "data": {
        "id": 1,
        "source": "Updated source",
        "category": {
            "id": 1,
            "name": "Salary"
        },
        "amount": 600.00,
        "date": "2023-12-15",
        "note": "Updated note",
        "updated_at": "2023-12-15T11:00:00Z"
    }
}
```

#### DELETE /api/income/{id}/

Delete an income transaction.

**Response:**
```json
{
    "status": "success",
    "message": "Income transaction deleted successfully",
    "data": {
        "id": 1,
        "source": "Deleted transaction",
        "amount": 500.00
    }
}
```

### Expense Transactions

#### GET /api/expense/

Get all expense transactions.

**Response:**
```json
{
    "status": "success",
    "data": {
        "transactions": [
            {
                "id": 1,
                "title": "Groceries",
                "amount": 150.00,
                "date": "2023-12-15",
                "created_at": "2023-12-15T10:00:00Z",
                "updated_at": "2023-12-15T10:00:00Z"
            }
        ],
        "stats": {
            "total": 2500.00,
            "count": 10
        }
    }
}
```

#### GET /api/expense/{id}/

Get a specific expense transaction.

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "title": "Groceries",
        "amount": 150.00,
        "date": "2023-12-15",
        "created_at": "2023-12-15T10:00:00Z",
        "updated_at": "2023-12-15T10:00:00Z"
    }
}
```

#### POST /api/expense/

Create a new expense transaction.

**Request Body:**
```json
{
    "title": "Restaurant",
    "amount": 75.00,
    "date": "2023-12-15"
}
```

**Response (201 Created):**
```json
{
    "status": "success",
    "message": "Expense transaction created successfully",
    "data": {
        "id": 2,
        "title": "Restaurant",
        "amount": 75.00,
        "date": "2023-12-15",
        "created_at": "2023-12-15T10:00:00Z"
    }
}
```

#### PUT /api/expense/{id}/

Update an existing expense transaction.

**Request Body (partial updates allowed):**
```json
{
    "title": "Updated title",
    "amount": 80.00
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Expense transaction updated successfully",
    "data": {
        "id": 1,
        "title": "Updated title",
        "amount": 80.00,
        "date": "2023-12-15",
        "updated_at": "2023-12-15T11:00:00Z"
    }
}
```

#### DELETE /api/expense/{id}/

Delete an expense transaction.

**Response:**
```json
{
    "status": "success",
    "message": "Expense transaction deleted successfully",
    "data": {
        "id": 1,
        "title": "Deleted expense",
        "amount": 75.00
    }
}
```

### All Transactions

#### GET /api/transactions/

Get all transactions (both income and expenses) combined.

**Response:**
```json
{
    "status": "success",
    "data": {
        "transactions": [
            {
                "id": 1,
                "type": "income",
                "title": "Salary",
                "category": {
                    "id": 1,
                    "name": "Salary"
                },
                "amount": 3000.00,
                "date": "2023-12-15",
                "note": "Monthly salary",
                "created_at": "2023-12-15T10:00:00Z",
                "updated_at": "2023-12-15T10:00:00Z"
            },
            {
                "id": 2,
                "type": "expense",
                "title": "Groceries",
                "category": {
                    "id": null,
                    "name": "Expense"
                },
                "amount": 150.00,
                "date": "2023-12-15",
                "note": "",
                "created_at": "2023-12-15T10:00:00Z",
                "updated_at": "2023-12-15T10:00:00Z"
            }
        ],
        "stats": {
            "totalIncome": 5000.00,
            "totalExpenses": 2500.00,
            "currentBalance": 2500.00,
            "totalTransactions": 15
        }
    }
}
```

### Categories

#### GET /api/categories/

Get all available income categories.

**Response:**
```json
{
    "status": "success",
    "data": {
        "categories": [
            {
                "id": 1,
                "name": "Salary",
                "created_at": "2023-12-01T10:00:00Z"
            },
            {
                "id": 2,
                "name": "Business",
                "created_at": "2023-12-01T10:00:00Z"
            },
            {
                "id": 3,
                "name": "Freelancing",
                "created_at": "2023-12-01T10:00:00Z"
            },
            {
                "id": 4,
                "name": "Investment",
                "created_at": "2023-12-01T10:00:00Z"
            }
        ],
        "count": 4
    }
}
```

## Error Responses

### Validation Errors (400 Bad Request)

```json
{
    "status": "error",
    "message": "Missing required field: amount"
}
```

### Not Found Errors (404 Not Found)

```json
{
    "status": "error",
    "message": "Income transaction not found"
}
```

### Server Errors (500 Internal Server Error)

```json
{
    "status": "error",
    "message": "Failed to create income transaction: Database connection error"
}
```

## Usage Examples

### JavaScript/AJAX Examples

#### Create Income Transaction

```javascript
fetch('/api/income/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        category_id: 1,
        source: 'Freelance Project',
        amount: 1500.00,
        date: '2023-12-15',
        note: 'Web development project'
    })
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log('Transaction created:', data.data);
    } else {
        console.error('Error:', data.message);
    }
});
```

#### Update Expense Transaction

```javascript
fetch('/api/expense/1/', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        title: 'Updated Expense Title',
        amount: 200.00
    })
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log('Transaction updated:', data.data);
    } else {
        console.error('Error:', data.message);
    }
});
```

#### Delete Transaction

```javascript
fetch('/api/income/1/', {
    method: 'DELETE'
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log('Transaction deleted:', data.data);
    } else {
        console.error('Error:', data.message);
    }
});
```

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in future versions.

## Versioning

The current API version is v1. Future versions will be accessible via `/api/v2/` etc.

## Support

For API support and questions, please refer to the project documentation or contact the development team.