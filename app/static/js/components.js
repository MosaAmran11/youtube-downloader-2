// Components JavaScript - Reusable UI components

// Snackbar functionality
let snackbarCounter = 0;

function showSnackbar(message, type = "info", title = "", duration = 5000) {
  const id = `snackbar-${++snackbarCounter}`;
  const container = document.getElementById("snackbar-container");

  // Define icons and colors for different types
  const typeConfig = {
    success: { icon: "check-circle", title: title || "Success" },
    error: { icon: "exclamation-triangle", title: title || "Error" },
    warning: { icon: "exclamation-circle", title: title || "Warning" },
    info: { icon: "info-circle", title: title || "Info" },
  };

  const config = typeConfig[type] || typeConfig.info;

  // Create snackbar element
  const snackbar = document.createElement("div");
  snackbar.className = `snackbar ${type}`;
  snackbar.id = id;
  snackbar.innerHTML = `
        <div class="snackbar-content">
            <div class="snackbar-icon">
                <i class="fas fa-${config.icon}"></i>
            </div>
            <div class="snackbar-message">
                <span class="snackbar-title">${config.title}</span>
                <span class="snackbar-text">${message}</span>
            </div>
            <button class="snackbar-close" onclick="closeSnackbar('${id}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="snackbar-progress"></div>
    `;

  // Add to container
  container.appendChild(snackbar);

  // Auto-remove after duration
  if (duration > 0) {
    setTimeout(() => {
      closeSnackbar(id);
    }, duration);
  }

  return id;
}

function closeSnackbar(id) {
  const snackbar = document.getElementById(id);
  if (snackbar) {
    snackbar.style.animation = "slideOut 0.3s ease forwards";
    setTimeout(() => {
      if (snackbar.parentNode) {
        snackbar.parentNode.removeChild(snackbar);
      }
    }, 300);
  }
}

// Close all snackbars
function closeAllSnackbars() {
  const container = document.getElementById("snackbar-container");
  if (container) {
    container.innerHTML = "";
  }
}

// Toast notification (simpler version of snackbar)
function showToast(message, type = "info", duration = 3000) {
  showSnackbar(message, type, "", duration);
}

// Confirmation dialog
function showConfirm(message, onConfirm, onCancel) {
  const id = `confirm-${++snackbarCounter}`;
  const container = document.getElementById("snackbar-container");

  const confirmSnackbar = document.createElement("div");
  confirmSnackbar.className = "snackbar warning";
  confirmSnackbar.id = id;
  confirmSnackbar.innerHTML = `
        <div class="snackbar-content">
            <div class="snackbar-icon">
                <i class="fas fa-question-circle"></i>
            </div>
            <div class="snackbar-message">
                <span class="snackbar-title">Confirm Action</span>
                <span class="snackbar-text">${message}</span>
            </div>
            <div class="snackbar-actions">
                <button class="btn btn-sm btn-success" onclick="confirmAction('${id}', true)">
                    <i class="fas fa-check"></i> Yes
                </button>
                <button class="btn btn-sm btn-secondary" onclick="confirmAction('${id}', false)">
                    <i class="fas fa-times"></i> No
                </button>
            </div>
        </div>
    `;

  container.appendChild(confirmSnackbar);

  // Store callbacks
  confirmSnackbar.dataset.onConfirm = onConfirm;
  confirmSnackbar.dataset.onCancel = onCancel;

  return id;
}

function confirmAction(id, confirmed) {
  const snackbar = document.getElementById(id);
  if (snackbar) {
    const callback = confirmed
      ? snackbar.dataset.onConfirm
      : snackbar.dataset.onCancel;

    closeSnackbar(id);

    if (callback && typeof window[callback] === "function") {
      window[callback]();
    }
  }
}

// Modal functionality
function showModal(title, content, buttons = []) {
  // Create modal HTML
  const modalHTML = `
        <div class="modal fade" id="customModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        ${buttons
                          .map(
                            (btn) => `
                            <button type="button" class="btn btn-${
                              btn.type || "secondary"
                            }" 
                                    onclick="${btn.onClick || "closeModal()"}">
                                ${btn.text}
                            </button>
                        `
                          )
                          .join("")}
                    </div>
                </div>
            </div>
        </div>
    `;

  // Remove existing modal
  const existingModal = document.getElementById("customModal");
  if (existingModal) {
    existingModal.remove();
  }

  // Add new modal
  document.body.insertAdjacentHTML("beforeend", modalHTML);

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("customModal"));
  modal.show();
}

function closeModal() {
  const modal = bootstrap.Modal.getInstance(
    document.getElementById("customModal")
  );
  if (modal) {
    modal.hide();
  }
}

// Tooltip initialization
function initTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// Popover initialization
function initPopovers() {
  const popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]')
  );
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
}

// Initialize components when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Bootstrap components
  initTooltips();
  initPopovers();

  // Add keyboard shortcuts
  document.addEventListener("keydown", function (e) {
    // Escape key closes snackbars
    if (e.key === "Escape") {
      closeAllSnackbars();
    }

    // Ctrl/Cmd + K shows keyboard shortcuts
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      showKeyboardShortcuts();
    }
  });
});

// Keyboard shortcuts modal
function showKeyboardShortcuts() {
  const shortcuts = [
    { key: "Escape", description: "Close all notifications" },
    { key: "Ctrl/Cmd + K", description: "Show keyboard shortcuts" },
    { key: "Ctrl/Cmd + Enter", description: "Submit current form" },
  ];

  const content = `
        <div class="keyboard-shortcuts">
            ${shortcuts
              .map(
                (shortcut) => `
                <div class="shortcut-item">
                    <kbd>${shortcut.key}</kbd>
                    <span>${shortcut.description}</span>
                </div>
            `
              )
              .join("")}
        </div>
    `;

  showModal("Keyboard Shortcuts", content, [
    { text: "Close", type: "secondary", onClick: "closeModal()" },
  ]);
}

// Add CSS for new components
const additionalCSS = `
    .snackbar-actions {
        display: flex;
        gap: 0.5rem;
        margin-left: 1rem;
    }
    
    .keyboard-shortcuts {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .shortcut-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 0.375rem;
    }
    
    .shortcut-item kbd {
        background: #343a40;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }
`;

// Inject additional CSS
const style = document.createElement("style");
style.textContent = additionalCSS;
document.head.appendChild(style);
