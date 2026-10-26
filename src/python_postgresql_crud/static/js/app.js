/**
 * Frontend JavaScript Controller for User Management CRUD
 * Interacts with FastAPI REST endpoints and PostgreSQL backend.
 */

// Application State
const state = {
  users: [],
  stats: null,
  page: 1,
  pageSize: 10,
  totalPages: 1,
  totalUsers: 0,
  search: '',
  hobby: '',
  gender: '',
  isActive: '',
  sortBy: 'created_at',
  sortOrder: 'desc',
  selectedHobbies: new Set(),
  editingUserId: null,
  deletingUserId: null,
  deletingUserName: '',
};

// DOM Content Loaded Entrypoint
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initEventListeners();
  checkBackendHealth();
  fetchStats();
  fetchUsers();
});

/* ==========================================================================
   1. Theme Management (Dark / Light Mode)
   ========================================================================== */
function initTheme() {
  const themeToggle = document.getElementById('theme-toggle');
  const lightIcon = document.getElementById('theme-toggle-light-icon');
  const darkIcon = document.getElementById('theme-toggle-dark-icon');

  function updateIcons() {
    const isDark = document.documentElement.classList.contains('dark');
    if (isDark) {
      lightIcon.classList.remove('hidden');
      darkIcon.classList.add('hidden');
    } else {
      lightIcon.classList.add('hidden');
      darkIcon.classList.remove('hidden');
    }
  }

  updateIcons();

  themeToggle.addEventListener('click', () => {
    if (document.documentElement.classList.contains('dark')) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('color-theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('color-theme', 'dark');
    }
    updateIcons();
  });
}

/* ==========================================================================
   2. Toast Notification Engine
   ========================================================================== */
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-enter pointer-events-auto flex items-center p-3.5 rounded-2xl shadow-xl text-xs font-semibold max-w-sm border backdrop-blur-md ${
    type === 'success'
      ? 'bg-emerald-50/95 dark:bg-emerald-950/90 text-emerald-800 dark:text-emerald-200 border-emerald-200 dark:border-emerald-800'
      : type === 'error'
      ? 'bg-rose-50/95 dark:bg-rose-950/90 text-rose-800 dark:text-rose-200 border-rose-200 dark:border-rose-800'
      : 'bg-indigo-50/95 dark:bg-indigo-950/90 text-indigo-800 dark:text-indigo-200 border-indigo-200 dark:border-indigo-800'
  }`;

  const icon = type === 'success' 
    ? `<svg class="w-4 h-4 mr-2 text-emerald-600 dark:text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`
    : `<svg class="w-4 h-4 mr-2 text-rose-600 dark:text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

  toast.innerHTML = `${icon} <span class="flex-1">${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('toast-enter');
    toast.classList.add('toast-leave');
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

/* ==========================================================================
   3. Backend Health Check
   ========================================================================== */
async function checkBackendHealth() {
  const badge = document.getElementById('db-status-badge');
  try {
    const res = await fetch('/health');
    if (!res.ok) throw new Error('Health check failed');
    const data = await res.json();
    if (data.database === 'connected') {
      badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>PostgreSQL Connected`;
      badge.className = 'hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800';
    } else {
      badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5"></span>DB Standby`;
      badge.className = 'hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800';
    }
  } catch {
    badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5"></span>API Offline`;
    badge.className = 'hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300 border border-rose-200 dark:border-rose-800';
  }
}

/* ==========================================================================
   4. Statistics Loading
   ========================================================================== */
async function fetchStats() {
  try {
    const res = await fetch('/api/v1/users/stats');
    if (!res.ok) return;
    const stats = await res.json();
    state.stats = stats;

    document.getElementById('stat-total-users').textContent = stats.total_users;
    document.getElementById('stat-active-users').textContent = stats.active_users;
    
    const activeRate = stats.total_users > 0 
      ? Math.round((stats.active_users / stats.total_users) * 100) 
      : 0;
    document.getElementById('stat-active-percent').textContent = `${activeRate}% active rate`;

    const topHobby = stats.top_hobbies && stats.top_hobbies.length > 0 
      ? stats.top_hobbies[0] 
      : null;
    
    document.getElementById('stat-top-hobby').textContent = topHobby ? topHobby.hobby : 'None yet';
    document.getElementById('stat-top-hobby-count').textContent = topHobby ? `${topHobby.count} users interested` : 'Most common interest';
    document.getElementById('stat-recent-users').textContent = stats.recent_users_count;
  } catch (err) {
    console.error('Error fetching statistics:', err);
  }
}

/* ==========================================================================
   5. User List Fetching & Table Rendering
   ========================================================================== */
async function fetchUsers() {
  const tbody = document.getElementById('users-table-body');
  const emptyState = document.getElementById('empty-state');
  const paginationContainer = document.getElementById('pagination-container');

  // Loading skeleton placeholder
  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="py-12 text-center text-slate-400">
        <div class="inline-flex items-center space-x-2">
          <svg class="animate-spin w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span class="text-xs font-medium">Loading user directory from PostgreSQL...</span>
        </div>
      </td>
    </tr>
  `;

  const queryParams = new URLSearchParams({
    page: state.page,
    page_size: state.pageSize,
    sort_by: state.sortBy,
    sort_order: state.sortOrder,
  });

  if (state.search) queryParams.set('search', state.search);
  if (state.hobby) queryParams.set('hobby', state.hobby);
  if (state.gender) queryParams.set('gender', state.gender);
  if (state.isActive !== '') queryParams.set('is_active', state.isActive);

  try {
    const res = await fetch(`/api/v1/users?${queryParams.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch users');
    const data = await res.json();

    state.users = data.items;
    state.totalPages = data.total_pages;
    state.totalUsers = data.total;

    if (data.items.length === 0) {
      tbody.innerHTML = '';
      emptyState.classList.remove('hidden');
      paginationContainer.classList.add('hidden');
    } else {
      emptyState.classList.add('hidden');
      paginationContainer.classList.remove('hidden');
      renderUsersTable(data.items);
      renderPagination(data);
    }
  } catch (err) {
    console.error('Failed to load users:', err);
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-8 text-center text-rose-500 text-xs">
          Unable to connect to PostgreSQL database. Make sure your database is running.
        </td>
      </tr>
    `;
    emptyState.classList.add('hidden');
    paginationContainer.classList.add('hidden');
  }
}

function renderUsersTable(users) {
  const tbody = document.getElementById('users-table-body');
  tbody.innerHTML = '';

  users.forEach((user) => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors group';

    // Avatar initial and gradient
    const initial = user.name ? user.name.charAt(0).toUpperCase() : 'U';
    const gradientIdx = Math.abs(hashCode(user.email || user.name)) % 6;

    // Hobbies badges
    const hobbiesHtml = (user.hobbies && user.hobbies.length > 0)
      ? user.hobbies.slice(0, 3).map(h => `
          <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-100 dark:border-indigo-800/60">
            ${escapeHtml(h)}
          </span>
        `).join('') + (user.hobbies.length > 3 ? `<span class="text-[10px] text-slate-400 font-semibold">+${user.hobbies.length - 3}</span>` : '')
      : '<span class="text-xs text-slate-400 italic">None</span>';

    // Location
    const location = [user.city, user.country].filter(Boolean).join(', ') || 'Not specified';

    // Status Badge
    const statusBadge = user.is_active
      ? `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
           <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>Active
         </span>`
      : `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
           <span class="w-1.5 h-1.5 rounded-full bg-slate-400 mr-1.5"></span>Inactive
         </span>`;

    // Date
    const createdDate = new Date(user.created_at).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });

    tr.innerHTML = `
      <td class="py-3.5 pl-6 pr-3">
        <div class="flex items-center space-x-3">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-bold shadow-sm avatar-gradient-${gradientIdx} shrink-0">
            ${initial}
          </div>
          <div class="min-w-0">
            <button onclick="openViewModal(${user.id})" class="text-sm font-semibold text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 truncate block text-left">
              ${escapeHtml(user.name)}
            </button>
            <div class="text-[11px] text-slate-400 capitalize">
              ${user.gender ? user.gender.replace(/_/g, ' ') : 'Prefer not to say'}
            </div>
          </div>
        </div>
      </td>
      <td class="py-3.5 px-3">
        <div class="text-xs text-slate-700 dark:text-slate-300 font-medium">${escapeHtml(user.email)}</div>
        <div class="text-[11px] text-slate-400 font-mono mt-0.5">${escapeHtml(user.mobile)}</div>
      </td>
      <td class="py-3.5 px-3">
        <div class="flex flex-wrap items-center gap-1 max-w-xs">
          ${hobbiesHtml}
        </div>
      </td>
      <td class="py-3.5 px-3">
        <div class="text-xs text-slate-600 dark:text-slate-400 flex items-center">
          <svg class="w-3.5 h-3.5 mr-1 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="truncate max-w-[130px]">${escapeHtml(location)}</span>
        </div>
      </td>
      <td class="py-3.5 px-3">
        ${statusBadge}
      </td>
      <td class="py-3.5 px-3 text-xs text-slate-500 dark:text-slate-400">
        ${createdDate}
      </td>
      <td class="py-3.5 pl-3 pr-6 text-right space-x-1 whitespace-nowrap">
        <button onclick="openViewModal(${user.id})" class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-slate-800 transition" title="View Profile">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </button>
        <button onclick="openEditModal(${user.id})" class="p-1.5 rounded-lg text-slate-400 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-slate-800 transition" title="Edit Profile">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button onclick="openDeleteModal(${user.id}, '${escapeJsString(user.name)}')" class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-slate-800 transition" title="Delete User">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderPagination(data) {
  const start = Math.min((data.page - 1) * data.page_size + 1, data.total);
  const end = Math.min(data.page * data.page_size, data.total);

  document.getElementById('pagination-start').textContent = data.total > 0 ? start : 0;
  document.getElementById('pagination-end').textContent = end;
  document.getElementById('pagination-total').textContent = data.total;

  const btnPrev = document.getElementById('btn-prev-page');
  const btnNext = document.getElementById('btn-next-page');

  btnPrev.disabled = !data.has_prev;
  btnNext.disabled = !data.has_next;

  const pageNumbersContainer = document.getElementById('pagination-page-numbers');
  pageNumbersContainer.innerHTML = '';

  for (let i = 1; i <= data.total_pages; i++) {
    // Show max 5 page buttons around current page
    if (i === 1 || i === data.total_pages || (i >= data.page - 2 && i <= data.page + 2)) {
      const pageBtn = document.createElement('button');
      pageBtn.className = `w-7 h-7 text-xs font-semibold rounded-lg transition ${
        i === data.page
          ? 'bg-indigo-600 text-white shadow-sm'
          : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
      }`;
      pageBtn.textContent = i;
      pageBtn.onclick = () => {
        state.page = i;
        fetchUsers();
      };
      pageNumbersContainer.appendChild(pageBtn);
    }
  }
}

/* ==========================================================================
   6. Modal Controls & Form Logic (Create & Edit)
   ========================================================================== */
function openCreateModal() {
  state.editingUserId = null;
  state.selectedHobbies.clear();

  document.getElementById('modal-title').textContent = 'Submit User Profile';
  document.getElementById('btn-save-text').textContent = 'Save Profile';
  document.getElementById('form-user-id').value = '';

  // Reset form inputs
  document.getElementById('user-form').reset();
  document.getElementById('form-country').value = 'India';
  document.getElementById('form-is-active').checked = true;

  updateHobbiesTagContainer();
  updatePillStyles();

  document.getElementById('user-modal').classList.remove('hidden');
}

async function openEditModal(userId) {
  try {
    const res = await fetch(`/api/v1/users/${userId}`);
    if (!res.ok) throw new Error('Could not fetch user details');
    const user = await res.json();

    state.editingUserId = userId;
    state.selectedHobbies = new Set(user.hobbies || []);

    document.getElementById('modal-title').textContent = 'Edit User Profile';
    document.getElementById('btn-save-text').textContent = 'Update Profile';
    document.getElementById('form-user-id').value = user.id;

    document.getElementById('form-name').value = user.name || '';
    document.getElementById('form-email').value = user.email || '';
    document.getElementById('form-mobile').value = user.mobile || '';
    document.getElementById('form-gender').value = user.gender || 'prefer_not_to_say';
    document.getElementById('form-dob').value = user.date_of_birth || '';
    document.getElementById('form-city').value = user.city || '';
    document.getElementById('form-country').value = user.country || 'India';
    document.getElementById('form-bio').value = user.bio || '';
    document.getElementById('form-is-active').checked = !!user.is_active;

    updateHobbiesTagContainer();
    updatePillStyles();

    document.getElementById('user-modal').classList.remove('hidden');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function closeUserModal() {
  document.getElementById('user-modal').classList.add('hidden');
  state.editingUserId = null;
  state.selectedHobbies.clear();
}

async function handleFormSubmit(e) {
  e.preventDefault();

  const btnSave = document.getElementById('btn-save-user');
  const spinner = document.getElementById('btn-save-spinner');
  btnSave.disabled = true;
  spinner.classList.remove('hidden');

  const payload = {
    name: document.getElementById('form-name').value.trim(),
    email: document.getElementById('form-email').value.trim(),
    mobile: document.getElementById('form-mobile').value.trim(),
    gender: document.getElementById('form-gender').value,
    hobbies: Array.from(state.selectedHobbies),
    date_of_birth: document.getElementById('form-dob').value || null,
    city: document.getElementById('form-city').value.trim() || null,
    country: document.getElementById('form-country').value.trim() || null,
    bio: document.getElementById('form-bio').value.trim() || null,
    is_active: document.getElementById('form-is-active').checked,
  };

  try {
    const isEdit = !!state.editingUserId;
    const url = isEdit ? `/api/v1/users/${state.editingUserId}` : '/api/v1/users';
    const method = isEdit ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      const errorMsg = data.detail || 'Validation failed. Please check your inputs.';
      throw new Error(errorMsg);
    }

    showToast(isEdit ? 'Profile updated successfully!' : 'User created successfully!', 'success');
    closeUserModal();
    fetchUsers();
    fetchStats();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btnSave.disabled = false;
    spinner.classList.add('hidden');
  }
}

/* ==========================================================================
   7. Hobbies Interactive Selector
   ========================================================================== */
function updateHobbiesTagContainer() {
  const container = document.getElementById('hobbies-tags-container');
  const input = document.getElementById('form-hobby-input');

  // Remove existing tags except input
  container.querySelectorAll('.hobby-tag').forEach(el => el.remove());

  state.selectedHobbies.forEach((hobby) => {
    const tag = document.createElement('span');
    tag.className = 'hobby-tag inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800';
    tag.innerHTML = `
      <span>${escapeHtml(hobby)}</span>
      <button type="button" class="ml-1 text-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-200" onclick="removeHobby('${escapeJsString(hobby)}')">
        &times;
      </button>
    `;
    container.insertBefore(tag, input);
  });
}

function updatePillStyles() {
  document.querySelectorAll('.hobby-pill').forEach(btn => {
    const hobby = btn.dataset.hobby;
    if (state.selectedHobbies.has(hobby)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

function toggleHobby(hobby) {
  if (state.selectedHobbies.has(hobby)) {
    state.selectedHobbies.delete(hobby);
  } else {
    state.selectedHobbies.add(hobby);
  }
  updateHobbiesTagContainer();
  updatePillStyles();
}

function removeHobby(hobby) {
  state.selectedHobbies.delete(hobby);
  updateHobbiesTagContainer();
  updatePillStyles();
}

/* ==========================================================================
   8. View User Details Modal
   ========================================================================== */
async function openViewModal(userId) {
  try {
    const res = await fetch(`/api/v1/users/${userId}`);
    if (!res.ok) throw new Error('User not found');
    const user = await res.json();

    document.getElementById('view-name').textContent = user.name;
    document.getElementById('view-email').textContent = user.email;
    document.getElementById('view-mobile').textContent = user.mobile;
    document.getElementById('view-gender').textContent = user.gender ? user.gender.replace(/_/g, ' ') : 'N/A';
    document.getElementById('view-dob').textContent = user.date_of_birth || 'Not specified';
    document.getElementById('view-location').textContent = [user.city, user.country].filter(Boolean).join(', ') || 'Not specified';
    document.getElementById('view-bio').textContent = user.bio || 'No personal bio added yet.';

    const initial = user.name ? user.name.charAt(0).toUpperCase() : 'U';
    document.getElementById('view-avatar').textContent = initial;

    const statusBadge = document.getElementById('view-status-badge');
    statusBadge.innerHTML = user.is_active
      ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">Active</span>'
      : '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-300">Inactive</span>';

    // Hobbies chips
    const hobbiesContainer = document.getElementById('view-hobbies');
    hobbiesContainer.innerHTML = '';
    if (user.hobbies && user.hobbies.length > 0) {
      user.hobbies.forEach(h => {
        const span = document.createElement('span');
        span.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800';
        span.textContent = h;
        hobbiesContainer.appendChild(span);
      });
    } else {
      hobbiesContainer.innerHTML = '<span class="text-xs text-slate-400 italic">No hobbies recorded.</span>';
    }

    document.getElementById('view-created-at').textContent = new Date(user.created_at).toLocaleString();
    document.getElementById('view-updated-at').textContent = new Date(user.updated_at).toLocaleString();

    document.getElementById('btn-view-edit').onclick = () => {
      closeViewModal();
      openEditModal(user.id);
    };

    document.getElementById('view-modal').classList.remove('hidden');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function closeViewModal() {
  document.getElementById('view-modal').classList.add('hidden');
}

/* ==========================================================================
   9. Delete Confirmation Modal
   ========================================================================== */
function openDeleteModal(userId, userName) {
  state.deletingUserId = userId;
  state.deletingUserName = userName;
  document.getElementById('delete-user-name').textContent = `"${userName}"`;
  document.getElementById('delete-modal').classList.remove('hidden');
}

function closeDeleteModal() {
  document.getElementById('delete-modal').classList.add('hidden');
  state.deletingUserId = null;
}

async function confirmDelete() {
  if (!state.deletingUserId) return;

  try {
    const res = await fetch(`/api/v1/users/${state.deletingUserId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete user.');

    showToast(`User "${state.deletingUserName}" was removed.`, 'success');
    closeDeleteModal();
    fetchUsers();
    fetchStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/* ==========================================================================
   10. Sample Data Seeding
   ========================================================================== */
async function seedSampleData() {
  const btn = document.getElementById('btn-seed-data');
  btn.disabled = true;

  try {
    const res = await fetch('/api/v1/users/seed', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Seeding failed');

    showToast(data.message || 'Sample users seeded successfully!', 'success');
    fetchUsers();
    fetchStats();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
  }
}

/* ==========================================================================
   11. Event Listeners Setup
   ========================================================================== */
function initEventListeners() {
  // Modal openers
  document.getElementById('btn-open-create-modal').addEventListener('click', openCreateModal);
  document.getElementById('btn-close-modal').addEventListener('click', closeUserModal);
  document.getElementById('btn-cancel-modal').addEventListener('click', closeUserModal);

  // Form submit
  document.getElementById('user-form').addEventListener('submit', handleFormSubmit);

  // View modal closers
  document.getElementById('btn-close-view-modal').addEventListener('click', closeViewModal);
  document.getElementById('btn-view-close').addEventListener('click', closeViewModal);

  // Delete modal closers
  document.getElementById('btn-cancel-delete').addEventListener('click', closeDeleteModal);
  document.getElementById('btn-confirm-delete').addEventListener('click', confirmDelete);

  // Seeding button
  document.getElementById('btn-seed-data').addEventListener('click', seedSampleData);

  // Hobby pills click in form
  document.querySelectorAll('.hobby-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      toggleHobby(btn.dataset.hobby);
    });
  });

  // Custom hobby input Enter handling
  const hobbyInput = document.getElementById('form-hobby-input');
  hobbyInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const val = hobbyInput.value.trim().replace(/,/g, '');
      if (val) {
        state.selectedHobbies.add(val);
        updateHobbiesTagContainer();
        updatePillStyles();
        hobbyInput.value = '';
      }
    }
  });

  // Search input debouncing
  let searchTimeout = null;
  const searchInput = document.getElementById('filter-search');
  const clearSearchBtn = document.getElementById('btn-clear-search');

  searchInput.addEventListener('input', (e) => {
    const val = e.target.value;
    clearSearchBtn.classList.toggle('hidden', !val);

    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.search = val;
      state.page = 1;
      fetchUsers();
    }, 300);
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearSearchBtn.classList.add('hidden');
    state.search = '';
    state.page = 1;
    fetchUsers();
  });

  // Dropdown filters
  document.getElementById('filter-hobby').addEventListener('change', (e) => {
    state.hobby = e.target.value;
    state.page = 1;
    fetchUsers();
  });

  document.getElementById('filter-gender').addEventListener('change', (e) => {
    state.gender = e.target.value;
    state.page = 1;
    fetchUsers();
  });

  document.getElementById('filter-status').addEventListener('change', (e) => {
    state.isActive = e.target.value;
    state.page = 1;
    fetchUsers();
  });

  // Pagination buttons
  document.getElementById('btn-prev-page').addEventListener('click', () => {
    if (state.page > 1) {
      state.page -= 1;
      fetchUsers();
    }
  });

  document.getElementById('btn-next-page').addEventListener('click', () => {
    if (state.page < state.totalPages) {
      state.page += 1;
      fetchUsers();
    }
  });

  // Table header sorting
  document.querySelectorAll('th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.sort;
      if (state.sortBy === col) {
        state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        state.sortBy = col;
        state.sortOrder = 'asc';
      }
      fetchUsers();
    });
  });
}

/* ==========================================================================
   12. Utilities & Sanitization
   ========================================================================== */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeJsString(str) {
  if (!str) return '';
  return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return hash;
}
