// Form validation and interaction JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // Initialize form validation
  initializeFormValidation();

  // Initialize date pickers
  initializeDatePickers();

  // Initialize real-time validation
  initializeRealTimeValidation();

  // Initialize form enhancements
  initializeFormEnhancements();

  console.log('Forms JavaScript initialized');
});

function initializeFormValidation() {
  // Enhanced client-side form validation
  const forms = document.querySelectorAll('.needs-validation, form');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (event) {
      // Custom validation logic
      const isValid = validateForm(form);

      if (!isValid || !form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        showFormErrors(form);
      } else {
        // Show loading state on submit
        showFormLoading(form);
      }

      form.classList.add('was-validated');
    });
  });
}

function initializeDatePickers() {
  // Enhanced date picker initialization
  const dateInputs = document.querySelectorAll('input[type="date"]');

  dateInputs.forEach(function (input) {
    // Set default date to today if empty
    if (!input.value) {
      input.value = new Date().toISOString().split('T')[0];
    }

    // Add date validation
    input.addEventListener('change', function () {
      validateDateInput(this);
    });

    // Add visual enhancements
    input.addEventListener('focus', function () {
      this.parentElement.classList.add('date-focused');
    });

    input.addEventListener('blur', function () {
      this.parentElement.classList.remove('date-focused');
    });
  });
}

function initializeRealTimeValidation() {
  // Real-time validation for amount fields
  const amountInputs = document.querySelectorAll('input[type="number"], input[name*="amount"]');

  amountInputs.forEach(input => {
    input.addEventListener('input', function () {
      validateAmountInput(this);
    });

    input.addEventListener('blur', function () {
      formatAmountInput(this);
    });
  });

  // Real-time validation for required text fields
  const textInputs = document.querySelectorAll('input[type="text"], input[type="email"], textarea');

  textInputs.forEach(input => {
    if (input.hasAttribute('required')) {
      input.addEventListener('input', function () {
        validateRequiredInput(this);
      });
    }
  });
}

function initializeFormEnhancements() {
  // Add floating label effects
  const formGroups = document.querySelectorAll('.form-floating, .form-group');

  formGroups.forEach(group => {
    const input = group.querySelector('input, textarea, select');
    if (input) {
      input.addEventListener('focus', function () {
        group.classList.add('focused');
      });

      input.addEventListener('blur', function () {
        group.classList.remove('focused');
        if (!this.value) {
          group.classList.remove('filled');
        } else {
          group.classList.add('filled');
        }
      });

      // Initial state
      if (input.value) {
        group.classList.add('filled');
      }
    }
  });

  // Add character counter for text areas
  const textAreas = document.querySelectorAll('textarea[maxlength]');
  textAreas.forEach(textarea => {
    addCharacterCounter(textarea);
  });
}

function validateForm(form) {
  let isValid = true;
  const errors = [];

  // Validate amount fields
  const amountInputs = form.querySelectorAll('input[type="number"], input[name*="amount"]');
  amountInputs.forEach(input => {
    if (!validateAmountInput(input)) {
      isValid = false;
      errors.push(`${getFieldLabel(input)} must be a positive number`);
    }
  });

  // Validate required fields
  const requiredInputs = form.querySelectorAll('input[required], textarea[required], select[required]');
  requiredInputs.forEach(input => {
    if (!validateRequiredInput(input)) {
      isValid = false;
      errors.push(`${getFieldLabel(input)} is required`);
    }
  });

  // Validate date fields
  const dateInputs = form.querySelectorAll('input[type="date"]');
  dateInputs.forEach(input => {
    if (!validateDateInput(input)) {
      isValid = false;
      errors.push(`${getFieldLabel(input)} must be a valid date`);
    }
  });

  if (!isValid) {
    console.log('Form validation errors:', errors);
  }

  return isValid;
}

function validateAmountInput(input) {
  const value = parseFloat(input.value);
  const isValid = !isNaN(value) && value > 0;

  updateFieldValidation(input, isValid, 'Amount must be greater than 0');
  return isValid;
}

function validateRequiredInput(input) {
  const value = input.value.trim();
  const isValid = value.length > 0;

  updateFieldValidation(input, isValid, 'This field is required');
  return isValid;
}

function validateDateInput(input) {
  const value = input.value;
  const isValid = value && !isNaN(new Date(value).getTime());

  updateFieldValidation(input, isValid, 'Please enter a valid date');
  return isValid;
}

function updateFieldValidation(input, isValid, errorMessage) {
  const formGroup = input.closest('.form-group, .form-floating, .mb-3');
  const feedback = formGroup?.querySelector('.invalid-feedback');

  if (isValid) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
  } else {
    input.classList.remove('is-valid');
    input.classList.add('is-invalid');

    if (feedback) {
      feedback.textContent = errorMessage;
    }
  }
}

function formatAmountInput(input) {
  const value = parseFloat(input.value);
  if (!isNaN(value) && value > 0) {
    input.value = value.toFixed(2);
  }
}

function addCharacterCounter(textarea) {
  const maxLength = parseInt(textarea.getAttribute('maxlength'));
  const counter = document.createElement('small');
  counter.className = 'form-text text-muted character-counter';

  const updateCounter = () => {
    const remaining = maxLength - textarea.value.length;
    counter.textContent = `${remaining} characters remaining`;

    if (remaining < 20) {
      counter.classList.add('text-warning');
      counter.classList.remove('text-muted');
    } else {
      counter.classList.add('text-muted');
      counter.classList.remove('text-warning');
    }
  };

  textarea.addEventListener('input', updateCounter);
  textarea.parentElement.appendChild(counter);
  updateCounter();
}

function showFormErrors(form) {
  const firstInvalidField = form.querySelector('.is-invalid');
  if (firstInvalidField) {
    firstInvalidField.focus();
    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function showFormLoading(form) {
  const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
  if (submitBtn) {
    const originalText = submitBtn.innerHTML || submitBtn.value;
    submitBtn.disabled = true;

    if (submitBtn.tagName === 'BUTTON') {
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    } else {
      submitBtn.value = 'Processing...';
    }

    // Store original text for potential restoration
    submitBtn.dataset.originalText = originalText;
  }
}

function getFieldLabel(input) {
  const label = input.closest('.form-group, .form-floating')?.querySelector('label');
  return label?.textContent?.replace('*', '').trim() || input.name || 'Field';
}

// Enhanced validation helper functions
function validateAmount(amount) {
  const num = parseFloat(amount);
  return !isNaN(num) && num > 0 && isFinite(num);
}

function validateRequiredField(field) {
  return typeof field === 'string' && field.trim().length > 0;
}

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validateDate(dateString) {
  const date = new Date(dateString);
  return !isNaN(date.getTime()) && dateString === date.toISOString().split('T')[0];
}

// Export functions for use in other scripts
window.formUtils = {
  validateAmount,
  validateRequiredField,
  validateEmail,
  validateDate,
  showFormLoading,
  updateFieldValidation
};