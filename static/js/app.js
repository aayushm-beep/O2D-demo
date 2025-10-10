// App Initialization - Compact UI with Theme Support
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initTheme();
  initNotifications();
});

// Sidebar Management
function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  const headerToggle = document.getElementById('headerSidebarToggle');
  
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      handleSidebarToggle();
    });
  }
  
  if (headerToggle) {
    headerToggle.addEventListener('click', () => {
      handleSidebarToggle();
    });
  }
  
  // Restore sidebar state
  const savedState = localStorage.getItem('sidebarCollapsed');
  if (savedState === 'true' && sidebar && window.innerWidth > 1024) {
    sidebar.classList.add('collapsed');
    const mainContent = document.getElementById('mainContent');
    if (mainContent) mainContent.classList.add('expanded');
  }
  
  // Close sidebar on mobile when clicking outside
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 1024 && 
        sidebar && 
        sidebar.classList.contains('show') && 
        !sidebar.contains(e.target) && 
        !e.target.closest('.mobile-menu-btn') &&
        !headerToggle?.contains(e.target)) {
      sidebar.classList.remove('show');
    }
  });

  // Handle window resize
  window.addEventListener('resize', () => {
    if (window.innerWidth > 1024 && sidebar) {
      sidebar.classList.remove('show');
    }
  });
}

function handleSidebarToggle() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  
  if (!sidebar) return;
  
  if (window.innerWidth <= 1024) {
    sidebar.classList.toggle('show');
  } else {
    sidebar.classList.toggle('collapsed');
    if (mainContent) mainContent.classList.toggle('expanded');
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
  }
}

// Theme Management
function initTheme() {
  const themeToggle = document.getElementById('themeToggle');
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon(currentTheme);
  
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
      
      // Smooth transition
      document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
      
      // Animate theme toggle button
      themeToggle.style.transition = 'transform 0.3s ease';
      themeToggle.style.transform = 'rotate(360deg)';
      setTimeout(() => {
        themeToggle.style.transform = '';
      }, 300);

      // Show toast
      showToast(`Switched to ${newTheme} mode`, 'success');
    });
  }
}

function updateThemeIcon(theme) {
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    const icon = themeToggle.querySelector('i');
    if (icon) {
      icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
  }
}

// Notification System
function initNotifications() {
  const notificationBtn = document.getElementById('notificationBtn');
  
  if (notificationBtn) {
    notificationBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      showNotificationPanel();
    });
  }
}

function showNotificationPanel() {
  // Remove existing panel if any
  const existingPanel = document.querySelector('.notification-panel');
  if (existingPanel) {
    existingPanel.remove();
    return;
  }

  const panel = document.createElement('div');
  panel.className = 'notification-panel';
  panel.innerHTML = `
    <div class="notification-header">
      <h3>Notifications</h3>
      <button onclick="this.closest('.notification-panel').remove()">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="notification-body">
      <div class="notification-item unread">
        <i class="fas fa-shopping-cart"></i>
        <div>
          <p><strong>New Order #ORD12345</strong></p>
          <span>2 minutes ago</span>
        </div>
      </div>
      <div class="notification-item unread">
        <i class="fas fa-truck"></i>
        <div>
          <p><strong>Shipment Delivered</strong></p>
          <span>1 hour ago</span>
        </div>
      </div>
      <div class="notification-item">
        <i class="fas fa-exclamation-triangle"></i>
        <div>
          <p><strong>Low Stock Alert</strong></p>
          <span>3 hours ago</span>
        </div>
      </div>
    </div>
    <div class="notification-footer">
      <a href="#" onclick="event.preventDefault(); showToast('Feature coming soon!', 'info');">View All Notifications</a>
    </div>
  `;
  
  document.body.appendChild(panel);
  
  setTimeout(() => {
    panel.classList.add('show');
  }, 10);
  
  // Close on outside click
  setTimeout(() => {
    document.addEventListener('click', function closePanel(e) {
      if (!panel.contains(e.target) && !e.target.closest('#notificationBtn')) {
        panel.classList.remove('show');
        setTimeout(() => panel.remove(), 300);
        document.removeEventListener('click', closePanel);
      }
    });
  }, 100);
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  };
  
  toast.innerHTML = `
    <i class="fas ${icons[type]}"></i>
    <span>${escapeHtml(message)}</span>
    <button onclick="this.parentElement.remove()" aria-label="Close">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toastContainer';
  container.className = 'toast-container';
  document.body.appendChild(container);
  return container;
}

// Utility Functions
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0);
}

function formatDate(date) {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

function formatDateTime(date) {
  if (!date) return 'N/A';
  return new Date(date).toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Debounce function for search
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Loading state management
function showLoading(element) {
  if (element) {
    element.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;gap:0.75rem;padding:1.5rem;">
        <div class="spinner"></div>
        <p style="color:var(--text-secondary);font-size:0.813rem;">Loading...</p>
      </div>
    `;
  } else {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'flex';
  }
}

function hideLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.style.display = 'none';
}

// Error handling
function handleError(error, userMessage = 'An error occurred') {
  console.error('Error:', error);
  showToast(userMessage, 'error');
}

// Confirm dialog
function confirmAction(message) {
  return new Promise((resolve) => {
    const modal = document.createElement('div');
    modal.className = 'confirm-modal';
    modal.innerHTML = `
      <div class="confirm-overlay"></div>
      <div class="confirm-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Confirm Action</h3>
        <p>${escapeHtml(message)}</p>
        <div class="confirm-actions">
          <button class="btn btn-secondary" onclick="window.confirmResolve(false); this.closest('.confirm-modal').remove()">
            Cancel
          </button>
          <button class="btn btn-primary" onclick="window.confirmResolve(true); this.closest('.confirm-modal').remove()">
            Confirm
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
    
    window.confirmResolve = resolve;
  });
}

// Add CSS for notifications and modals dynamically
const dynamicStyles = `
/* Notification Panel */
.notification-panel {
  position: fixed;
  top: 56px;
  right: 16px;
  width: 300px;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xl);
  z-index: 1000;
  transform: translateX(320px);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--border);
}

.notification-panel.show {
  transform: translateX(0);
  opacity: 1;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
}

.notification-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}

.notification-header button {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--radius-sm);
  transition: var(--transition-fast);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-header button:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.notification-body {
  max-height: 320px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-light);
  transition: var(--transition-fast);
  cursor: pointer;
}

.notification-item:hover {
  background: var(--bg-secondary);
}

.notification-item.unread {
  background: rgba(0, 102, 204, 0.04);
}

.notification-item i {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg-secondary);
  color: var(--primary);
  font-size: 0.875rem;
  flex-shrink: 0;
}

.notification-item p {
  margin: 0 0 0.188rem 0;
  font-size: 0.75rem;
  line-height: 1.4;
}

.notification-item span {
  font-size: 0.688rem;
  color: var(--text-secondary);
}

.notification-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border);
  text-align: center;
}

.notification-footer a {
  color: var(--primary);
  text-decoration: none;
  font-size: 0.75rem;
  font-weight: 600;
}

.notification-footer a:hover {
  text-decoration: underline;
}

/* Confirm Modal */
.confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.confirm-modal.show {
  opacity: 1;
}

.confirm-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
}

.confirm-content {
  position: relative;
  background: var(--bg-primary);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  max-width: 360px;
  width: calc(100% - 2rem);
  text-align: center;
  box-shadow: var(--shadow-xl);
}

.confirm-content i {
  font-size: 2.5rem;
  color: var(--warning);
  margin-bottom: 0.75rem;
}

.confirm-content h3 {
  margin-bottom: 0.375rem;
  font-size: 1.125rem;
}

.confirm-content p {
  color: var(--text-secondary);
  margin-bottom: 1.125rem;
  font-size: 0.875rem;
}

.confirm-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}
`;

// Inject styles
if (!document.getElementById('app-dynamic-styles')) {
  const styleEl = document.createElement('style');
  styleEl.id = 'app-dynamic-styles';
  styleEl.textContent = dynamicStyles;
  document.head.appendChild(styleEl);
}

// Export utilities globally
window.showToast = showToast;
window.confirmAction = confirmAction;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.debounce = debounce;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.handleError = handleError;
window.escapeHtml = escapeHtml;
window.toggleSidebar = handleSidebarToggle;