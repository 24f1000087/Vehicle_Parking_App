/**
 * Vehicle Parking App - Main Application
 * All components defined as JavaScript objects for CDN Vue compatibility
 */

// Check if Vue is loaded
if (typeof Vue === 'undefined') {
  console.error('Vue.js is not loaded!');
  document.getElementById('app').innerHTML = '<div class="container mt-5"><div class="alert alert-danger"><h4>Vue.js Error</h4><p>Vue.js is not loaded. Please refresh the page.</p></div></div>';
} else {
  console.log('Vue.js loaded successfully');
}

const { createApp } = Vue;
const API_BASE_URL = 'http://localhost:5000/api';

// Helper function to get auth headers
function getAuthHeaders() {
  return {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  };
}

// Login Component
const Login = {
  template: `
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header bg-primary text-white">
              <h3 class="text-center mb-0">Vehicle Parking App</h3>
            </div>
            <div class="card-body">
              <ul class="nav nav-tabs mb-3">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: isLogin }" @click.prevent="isLogin = true" href="#">Login</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: !isLogin }" @click.prevent="isLogin = false" href="#">Register</a>
                </li>
              </ul>
              <div v-if="isLogin">
                <form @submit.prevent="handleLogin">
                  <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" v-model="loginForm.username" required />
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" v-model="loginForm.password" required />
                  </div>
                  <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                    {{ loading ? 'Logging in...' : 'Login' }}
                  </button>
                </form>
              </div>
              <div v-if="!isLogin">
                <form @submit.prevent="handleRegister">
                  <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" v-model="registerForm.username" required />
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" v-model="registerForm.password" required />
                  </div>
                  <button type="submit" class="btn btn-success w-100" :disabled="loading">
                    {{ loading ? 'Registering...' : 'Register' }}
                  </button>
                </form>
              </div>
              <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      isLogin: true,
      loading: false,
      error: '',
      loginForm: { username: '', password: '' },
      registerForm: { username: '', password: '' }
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = '';
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/login`, this.loginForm);
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        this.$emit('login', response.data.user, response.data.access_token);
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed';
      } finally {
        this.loading = false;
      }
    },
    async handleRegister() {
      this.loading = true;
      this.error = '';
      try {
        await axios.post(`${API_BASE_URL}/auth/register`, this.registerForm);
        alert('Registration successful! Please login.');
        this.isLogin = true;
        this.loginForm.username = this.registerForm.username;
        this.registerForm = { username: '', password: '' };
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed';
      } finally {
        this.loading = false;
      }
    }
  }
};

// Admin Dashboard Component
const AdminDashboard = {
  template: `
    <div>
      <header class="app-header">
        <div class="brand-title">Parking App</div>
        <div class="d-flex align-items-center gap-3">
          <div class="text-end">
            <div class="small opacity-75 text-light">Role</div>
            <strong>System Admin</strong>
          </div>
          <button class="btn btn-outline-light btn-sm px-4" @click="handleLogout">Logout</button>
        </div>
      </header>

      <div class="admin-shell">
        <div class="admin-card">
          <div class="d-flex flex-wrap justify-content-between align-items-start gap-3">
            <div>
              <h2 class="mb-1">Admin Dashboard</h2>
              <p class="text-muted mb-0">Monitor every parking lot and occupancy in real-time</p>
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-outline-secondary" @click="refreshData">Refresh</button>
              <button class="btn btn-success" @click="openCreateModal">Create / Manage Lots</button>
            </div>
          </div>

          <ul class="nav dashboard-tabs nav-pills mt-4">
            <li class="nav-item" v-for="tab in tabs" :key="tab.value">
              <a class="nav-link" :class="{ active: activeTab === tab.value }" href="#" @click.prevent="setTab(tab.value)">
                {{ tab.label }}
              </a>
            </li>
          </ul>

          <div class="tab-content mt-4">
            <section v-if="activeTab === 'home'">
              <div class="summary-grid mb-4">
                <div class="summary-chip">
                  <p class="text-muted mb-1">Total Lots</p>
                  <h3 class="mb-0">{{ summary.total_lots || 0 }}</h3>
                </div>
                <div class="summary-chip">
                  <p class="text-muted mb-1">Total Spots</p>
                  <h3 class="mb-0">{{ summary.total_spots || 0 }}</h3>
                </div>
                <div class="summary-chip">
                  <p class="text-muted mb-1">Available</p>
                  <h3 class="mb-0 text-success">{{ summary.available_spots || 0 }}</h3>
                </div>
                <div class="summary-chip">
                  <p class="text-muted mb-1">Occupied</p>
                  <h3 class="mb-0 text-danger">{{ summary.occupied_spots || 0 }}</h3>
                </div>
              </div>

              <div v-if="parkingLots.length === 0" class="text-center text-muted py-5">
                No parking lots created yet. Use "Create / Manage Lots" to get started.
              </div>

              <div v-else>
                <div class="lot-card" v-for="lot in parkingLots" :key="lot.id">
                  <div class="lot-header">
                    <div>
                      <h5 class="mb-1">{{ lot.name }} <small class="text-muted">({{ lot.id }})</small></h5>
                      <p class="text-muted mb-0">{{ lot.address }}</p>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                      <span class="badge bg-dark fs-6">{{ formatCurrency(lot.price) }}/hr</span>
                      <button class="btn btn-outline-primary btn-sm" @click="editLot(lot)">Edit Lot</button>
                    </div>
                  </div>
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="small text-muted">
                      Available {{ lot.available_spots }} / {{ lot.number_of_spots }}
                    </div>
                    <button class="btn btn-link text-decoration-none p-0" @click="confirmDelete(lot)" :disabled="lot.occupied_spots > 0">
                      Delete Lot
                    </button>
                  </div>
                  <div class="spot-grid">
                    <button
                      v-for="spot in lot.spots"
                      :key="spot.id"
                      class="spot-chip"
                      :class="spot.status === 'A' ? 'spot-available' : 'spot-occupied'"
                      @click="openSpotDetails(spot)"
                    >
                      <span>{{ spot.status === 'A' ? 'A' : 'O' }}</span>
                      <small>{{ spot.spot_number }}</small>
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <section v-if="activeTab === 'summary'">
              <ChartsView :chartData="chartData" />
            </section>

            <section v-if="activeTab === 'users'">
              <div class="table-responsive">
                <table class="table align-middle">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Role</th>
                      <th>Created At</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id">
                      <td>{{ user.id }}</td>
                      <td>{{ user.username }}</td>
                      <td>
                        <span class="badge" :class="user.role === 'admin' ? 'bg-danger' : 'bg-primary'">{{ user.role }}</span>
                      </td>
                      <td>{{ formatDate(user.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section v-if="activeTab === 'search'">
              <div class="mb-4">
                <input type="search" class="form-control form-control-lg" placeholder="Search lot or address" v-model="searchTerm">
              </div>
              <div v-if="filteredLots.length === 0" class="text-muted text-center py-4">
                No parking lots match your search.
              </div>
              <div v-else>
                <div class="lot-card" v-for="lot in filteredLots" :key="lot.id">
                  <div class="lot-header">
                    <div>
                      <h5 class="mb-1">{{ lot.name }}</h5>
                      <p class="text-muted mb-0">{{ lot.address }}</p>
                    </div>
                    <span class="badge bg-dark fs-6">{{ formatCurrency(lot.price) }}/hr</span>
                  </div>
                  <div class="spot-grid">
                    <button
                      v-for="spot in lot.spots"
                      :key="spot.id"
                      class="spot-chip"
                      :class="spot.status === 'A' ? 'spot-available' : 'spot-occupied'"
                      @click="openSpotDetails(spot)"
                    >
                      <span>{{ spot.status === 'A' ? 'A' : 'O' }}</span>
                      <small>{{ spot.spot_number }}</small>
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>

      <div v-if="notification" class="alert notification-toast" :class="notification.type === 'success' ? 'alert-success' : 'alert-danger'">
        <div class="d-flex justify-content-between align-items-center">
          <div>{{ notification.message }}</div>
          <button type="button" class="btn-close" @click="notification = null"></button>
        </div>
      </div>

      <div class="modal fade show" style="display: block;" v-if="showLotModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ modalMode === 'edit' ? 'Edit Parking Lot' : 'Create Parking Lot' }}</h5>
              <button type="button" class="btn-close" @click="closeLotModal"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="saveLot">
                <div class="mb-3">
                  <label class="form-label">Name</label>
                  <input type="text" class="form-control" v-model="lotForm.name" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Address</label>
                  <input type="text" class="form-control" v-model="lotForm.address" required>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Price per Hour (₹)</label>
                    <input type="number" min="0" step="0.5" class="form-control" v-model="lotForm.price" required>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Spots</label>
                    <input type="number" class="form-control" v-model="lotForm.number_of_spots" :disabled="modalMode === 'edit'" min="1" required>
                  </div>
                </div>
                <div class="d-flex justify-content-end gap-2">
                  <button type="button" class="btn btn-outline-secondary" @click="closeLotModal">Cancel</button>
                  <button type="submit" class="btn btn-primary">{{ modalMode === 'edit' ? 'Save Changes' : 'Create Lot' }}</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div class="modal fade show" style="display: block;" v-if="showSpotDetails">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Spot Details</h5>
              <button type="button" class="btn-close" @click="closeSpotDetails"></button>
            </div>
            <div class="modal-body" v-if="loadingSpotDetails">
              <div class="text-center py-4">Loading...</div>
            </div>
            <div class="modal-body" v-else-if="selectedSpotDetails">
              <p class="mb-1"><strong>Status:</strong>
                <span class="badge" :class="selectedSpotDetails.spot.status === 'A' ? 'bg-success' : 'bg-danger'">
                  {{ selectedSpotDetails.spot.status === 'A' ? 'Available' : 'Occupied' }}
                </span>
              </p>
              <p class="mb-1"><strong>Spot:</strong> {{ selectedSpotDetails.spot.spot_number }}</p>
              <p class="mb-1"><strong>Lot:</strong> {{ selectedSpotDetails.lot?.name }}</p>
              <p class="mb-3"><strong>Price:</strong> {{ formatCurrency(selectedSpotDetails.lot?.price) }}/hr</p>
              <div v-if="selectedSpotDetails.reservation && selectedSpotDetails.user" class="border rounded p-3 bg-light">
                <h6 class="mb-2">Active Reservation</h6>
                <p class="mb-1"><strong>User:</strong> {{ selectedSpotDetails.user.username }}</p>
                <p class="mb-1"><strong>Start:</strong> {{ formatDate(selectedSpotDetails.reservation.start_time) }}</p>
                <p class="mb-0"><strong>Reservation ID:</strong> {{ selectedSpotDetails.reservation.id }}</p>
              </div>
              <div v-else class="text-muted">No vehicles parked in this spot right now.</div>
              <p class="text-danger small mt-3" v-if="selectedSpotDetails.spot.status === 'O'">
                Cannot delete an occupied spot
              </p>
            </div>
            <div class="modal-body" v-else>
              <div class="text-center text-muted py-4">Spot details unavailable.</div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="closeSpotDetails">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      tabs: [
        { label: 'Home', value: 'home' },
        { label: 'Summary', value: 'summary' },
        { label: 'Users', value: 'users' },
        { label: 'Search', value: 'search' }
      ],
      activeTab: 'home',
      parkingLots: [],
      users: [],
      summary: {},
      chartData: {},
      notification: null,
      lotForm: { name: '', address: '', price: '', number_of_spots: '' },
      showLotModal: false,
      modalMode: 'create',
      editingLotId: null,
      searchTerm: '',
      showSpotDetails: false,
      selectedSpotDetails: null,
      loadingSpotDetails: false
    };
  },
  computed: {
    filteredLots() {
      if (!this.searchTerm) {
        return this.parkingLots;
      }
      const term = this.searchTerm.toLowerCase();
      return this.parkingLots.filter(lot => `${lot.name} ${lot.address}`.toLowerCase().includes(term));
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      await Promise.all([this.loadSummary(), this.loadParkingLots(), this.loadUsers()]);
      if (this.activeTab === 'summary') {
        await this.loadChartData();
      }
    },
    async loadSummary() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/summary`, getAuthHeaders());
        this.summary = response.data.summary || {};
      } catch (err) {
        this.handleError('refresh dashboard summary', err);
      }
    },
    async loadParkingLots() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/parking-lots`, getAuthHeaders());
        this.parkingLots = (response.data.parking_lots || []).map(lot => ({
          ...lot,
          spots: (lot.spots || []).sort((a, b) => a.spot_number.localeCompare(b.spot_number))
        }));
      } catch (err) {
        this.handleError('load parking lots', err);
      }
    },
    async loadUsers() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/users`, getAuthHeaders());
        this.users = response.data.users || [];
      } catch (err) {
        this.handleError('fetch users', err);
      }
    },
    async loadChartData() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/charts`, getAuthHeaders());
        this.chartData = response.data || {};
      } catch (err) {
        this.handleError('load charts', err);
      }
    },
    setTab(tab) {
      this.activeTab = tab;
      if (tab === 'summary') {
        this.loadChartData();
      }
    },
    refreshData() {
      this.loadData();
      this.showNotification('Dashboard refreshed successfully', 'success');
    },
    openCreateModal() {
      this.modalMode = 'create';
      this.lotForm = { name: '', address: '', price: '', number_of_spots: '' };
      this.showLotModal = true;
      this.editingLotId = null;
    },
    editLot(lot) {
      this.modalMode = 'edit';
      this.editingLotId = lot.id;
      this.lotForm = {
        name: lot.name,
        address: lot.address,
        price: lot.price,
        number_of_spots: lot.number_of_spots
      };
      this.showLotModal = true;
    },
    async saveLot() {
      try {
        if (this.modalMode === 'edit' && this.editingLotId) {
          await axios.put(`${API_BASE_URL}/admin/parking-lots/${this.editingLotId}`, this.lotForm, getAuthHeaders());
          this.showNotification('Lot updated successfully', 'success');
        } else {
          await axios.post(`${API_BASE_URL}/admin/parking-lots`, this.lotForm, getAuthHeaders());
          this.showNotification('Lot created successfully', 'success');
        }
        this.closeLotModal();
        await this.loadParkingLots();
        await this.loadSummary();
      } catch (err) {
        this.handleError('save parking lot', err);
      }
    },
    confirmDelete(lot) {
      if (lot.occupied_spots > 0) {
        this.showNotification('Vacate all spots before deleting this lot');
        return;
      }
      if (confirm(`Delete ${lot.name}? This action cannot be undone.`)) {
        this.deleteLot(lot.id);
      }
    },
    async deleteLot(lotId) {
      try {
        await axios.delete(`${API_BASE_URL}/admin/parking-lots/${lotId}`, getAuthHeaders());
        this.showNotification('Parking lot deleted', 'success');
        await this.loadParkingLots();
        await this.loadSummary();
      } catch (err) {
        this.handleError('delete parking lot', err);
      }
    },
    closeLotModal() {
      this.showLotModal = false;
      this.modalMode = 'create';
      this.lotForm = { name: '', address: '', price: '', number_of_spots: '' };
      this.editingLotId = null;
    },
    async openSpotDetails(spot) {
      this.showSpotDetails = true;
      this.loadingSpotDetails = true;
      this.selectedSpotDetails = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/spots/${spot.id}/details`, getAuthHeaders());
        this.selectedSpotDetails = response.data;
      } catch (err) {
        this.handleError('fetch spot details', err);
        this.showSpotDetails = false;
      } finally {
        this.loadingSpotDetails = false;
      }
    },
    closeSpotDetails() {
      this.showSpotDetails = false;
      this.selectedSpotDetails = null;
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleString();
    },
    formatCurrency(value) {
      const amount = Number(value) || 0;
      return `₹${amount.toFixed(1)}`;
    },
    showNotification(message, type = 'danger') {
      this.notification = { message, type };
      setTimeout(() => {
        this.notification = null;
      }, 4000);
    },
    handleError(context, err) {
      console.error(`Unable to ${context}`, err);
      const fallback = err.response?.data?.error || err.message || 'Something went wrong';
      this.showNotification(`${context.charAt(0).toUpperCase() + context.slice(1)} failed. ${fallback}`);
    },
    handleLogout() {
      this.$emit('logout');
    }
  }
};

// User Dashboard Component
const UserDashboard = {
  template: `
    <div>
      <header class="app-header">
        <div class="brand-title">Parking App</div>
        <div class="d-flex align-items-center gap-3">
          <div class="text-end">
            <div class="small opacity-75 text-light">User</div>
            <strong>{{ currentUser?.username || 'User' }}</strong>
          </div>
          <button class="btn btn-outline-light btn-sm px-4" @click="handleLogout">Logout</button>
        </div>
      </header>

      <div class="admin-shell">
        <div class="user-card">
          <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-3">
            <div>
              <h2 class="mb-1">User Dashboard</h2>
              <p class="text-muted mb-0">Choose an available lot and we will assign the first free spot.</p>
            </div>
            <div>
              <button class="btn btn-success" @click="exportCSV">Export History</button>
            </div>
          </div>

          <div v-if="activeReservation" class="alert alert-info d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-1">Currently Parked</h5>
              <p class="mb-0">
                Spot <strong>{{ activeReservation.spot_number }}</strong> at <strong>{{ activeReservation.lot_name }}</strong><br>
                Started {{ formatDate(activeReservation.start_time) }}
              </p>
            </div>
            <button class="btn btn-danger" @click="vacateSpot">Release Spot</button>
          </div>

          <div class="summary-grid mb-4">
            <div class="summary-chip">
              <p class="text-muted mb-1">Total Reservations</p>
              <h3 class="mb-0">{{ summary.total_reservations || 0 }}</h3>
            </div>
            <div class="summary-chip">
              <p class="text-muted mb-1">Completed Trips</p>
              <h3 class="mb-0">{{ summary.completed_reservations || 0 }}</h3>
            </div>
            <div class="summary-chip">
              <p class="text-muted mb-1">Total Hours</p>
              <h3 class="mb-0">{{ summary.total_hours || 0 }}</h3>
            </div>
            <div class="summary-chip">
              <p class="text-muted mb-1">Total Spend</p>
              <h3 class="mb-0">{{ formatCurrency(summary.total_spent || 0) }}</h3>
            </div>
          </div>

          <UserChartsView :chartData="chartData" class="mb-5" />

          <ul class="nav dashboard-tabs nav-pills">
            <li class="nav-item"><a class="nav-link" :class="{ active: activeTab === 'lots' }" @click.prevent="activeTab = 'lots'" href="#">Available Lots</a></li>
            <li class="nav-item"><a class="nav-link" :class="{ active: activeTab === 'reservations' }" @click.prevent="activeTab = 'reservations'" href="#">My Reservations</a></li>
          </ul>

          <div class="tab-content mt-4">
            <section v-if="activeTab === 'lots'">
              <div class="row g-4">
                <div class="col-md-6" v-for="lot in parkingLots" :key="lot.id">
                  <div class="lot-card h-100">
                    <div class="lot-header">
                      <div>
                        <h5 class="mb-1">{{ lot.name }}</h5>
                        <p class="text-muted mb-0">{{ lot.address }}</p>
                      </div>
                      <span class="badge bg-dark fs-6">{{ formatCurrency(lot.price) }}/hr</span>
                    </div>
                    <p class="text-muted mb-3">
                      Availability: <strong>{{ lot.available_spots }}</strong> / {{ lot.number_of_spots }}
                    </p>
                    <button class="btn btn-primary w-100" @click="bookSpot(lot.id)" :disabled="lot.available_spots === 0 || !!activeReservation">
                      {{ lot.available_spots === 0 ? 'Lot Full' : activeReservation ? 'Active reservation in progress' : 'Book First Available Spot' }}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <section v-if="activeTab === 'reservations'">
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Spot</th>
                      <th>Lot</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Cost</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="r in reservations" :key="r.id">
                      <td>{{ r.id }}</td>
                      <td>{{ r.spot_number || 'N/A' }}</td>
                      <td>{{ r.lot_name || 'N/A' }}</td>
                      <td>{{ formatDate(r.start_time) }}</td>
                      <td>{{ r.end_time ? formatDate(r.end_time) : 'Active' }}</td>
                      <td>{{ r.cost ? formatCurrency(r.cost) : 'Pending' }}</td>
                      <td>
                        <span class="badge" :class="r.status === 'active' ? 'bg-success' : 'bg-secondary'">{{ r.status }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        </div>
      </div>

      <div v-if="notification" class="alert notification-toast" :class="notification.type === 'success' ? 'alert-success' : 'alert-danger'">
        <div class="d-flex justify-content-between align-items-center">
          <div>{{ notification.message }}</div>
          <button type="button" class="btn-close" @click="notification = null"></button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      activeTab: 'lots',
      parkingLots: [],
      reservations: [],
      activeReservation: null,
      notification: null,
      summary: {},
      chartData: {},
      currentUser: JSON.parse(localStorage.getItem('user') || '{}')
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.loadParkingLots(),
        this.loadReservations(),
        this.loadSummary(),
        this.loadChartData()
      ]);
    },
    async loadParkingLots() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/parking-lots`, getAuthHeaders());
        this.parkingLots = response.data.parking_lots || [];
      } catch (err) {
        this.handleError('load parking lots', err);
      }
    },
    async loadReservations() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/reservations`, getAuthHeaders());
        this.reservations = response.data.reservations || [];
      } catch (err) {
        this.handleError('load reservations', err);
      }
    },
    async loadSummary() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/summary`, getAuthHeaders());
        this.summary = response.data.summary || {};
        this.activeReservation = this.summary.active_reservation;
      } catch (err) {
        this.handleError('load summary', err);
      }
    },
    async loadChartData() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/charts`, getAuthHeaders());
        this.chartData = response.data || {};
      } catch (err) {
        this.handleError('load usage charts', err);
      }
    },
    async bookSpot(lotId) {
      if (this.activeReservation) {
        this.showNotification('Release your current spot before booking another');
        return;
      }
      try {
        await axios.post(`${API_BASE_URL}/user/book`, { lot_id: lotId }, getAuthHeaders());
        this.showNotification('Spot allocated successfully!', 'success');
        await this.loadData();
      } catch (err) {
        this.handleError('book spot', err);
      }
    },
    async vacateSpot() {
      if (!confirm('Release your current spot?')) return;
      try {
        const response = await axios.post(`${API_BASE_URL}/user/vacate`, {}, getAuthHeaders());
        const cost = response.data?.reservation?.cost || 0;
        this.showNotification(`Spot released. Total cost: ${this.formatCurrency(cost)}`, 'success');
        await this.loadData();
      } catch (err) {
        this.handleError('vacate spot', err);
      }
    },
    async exportCSV() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/export-csv-sync`, { ...getAuthHeaders(), responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `reservations_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        this.showNotification('CSV exported successfully', 'success');
      } catch (err) {
        this.handleError('export CSV', err);
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleString();
    },
    formatCurrency(value) {
      const amount = Number(value) || 0;
      return `₹${amount.toFixed(1)}`;
    },
    showNotification(message, type = 'danger') {
      this.notification = { message, type };
      setTimeout(() => { this.notification = null; }, 4000);
    },
    handleError(context, err) {
      console.error(`Unable to ${context}`, err);
      const fallback = err.response?.data?.error || err.message || 'Please try again.';
      this.showNotification(`Unable to ${context}. ${fallback}`);
    },
    handleLogout() {
      this.$emit('logout');
    }
  }
};

// Charts View Component
const ChartsView = {
  template: `
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card chart-card">
            <div class="card-body">
              <h5 class="mb-3">Revenue by Lot</h5>
              <canvas ref="revenueByLotChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card chart-card">
            <div class="card-body">
              <h5 class="mb-3">Occupancy per Lot</h5>
              <canvas ref="occupancyChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-12">
          <div class="card chart-card">
            <div class="card-body">
              <h5 class="mb-3">Weekly Reservations Trend</h5>
              <canvas ref="reservationsChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  props: ['chartData'],
  mounted() {
    this.renderCharts();
  },
  watch: {
    chartData: { deep: true, handler() { this.renderCharts(); } }
  },
  methods: {
    renderCharts() {
      this.$nextTick(() => {
        this.renderReservationsChart();
        this.renderRevenueByLotChart();
        this.renderOccupancyChart();
      });
    },
    renderReservationsChart() {
      const ctx = this.$refs.reservationsChart;
      if (!ctx) return;
      if (this.reservationsChartInstance) this.reservationsChartInstance.destroy();
      const data = this.chartData.daily_reservations || [];
      this.reservationsChartInstance = new Chart(ctx, {
        type: 'line',
        data: { labels: data.map(d => d.date), datasets: [{ label: 'Reservations', data: data.map(d => d.count), borderColor: 'rgb(75, 192, 192)', backgroundColor: 'rgba(75, 192, 192, 0.2)', tension: 0.1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
      });
    },
    renderRevenueByLotChart() {
      const ctx = this.$refs.revenueByLotChart;
      if (!ctx) return;
      if (this.revenueByLotInstance) this.revenueByLotInstance.destroy();
      const data = this.chartData.lot_revenue || [];
      this.revenueByLotInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.map(d => d.lot_name),
          datasets: [{
            data: data.map(d => d.revenue),
            backgroundColor: ['#22c55e', '#0ea5e9', '#a855f7', '#f97316', '#ef4444', '#14b8a6']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
      });
    },
    renderOccupancyChart() {
      const ctx = this.$refs.occupancyChart;
      if (!ctx) return;
      if (this.occupancyChartInstance) this.occupancyChartInstance.destroy();
      const data = this.chartData.lot_occupancy || [];
      this.occupancyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(d => d.lot_name),
          datasets: [
            { label: 'Occupied', data: data.map(d => d.occupied), backgroundColor: 'rgba(255, 99, 132, 0.5)', borderColor: 'rgba(255, 99, 132, 1)', borderWidth: 1 },
            { label: 'Available', data: data.map(d => d.available), backgroundColor: 'rgba(75, 192, 192, 0.5)', borderColor: 'rgba(75, 192, 192, 1)', borderWidth: 1 }
          ]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
      });
    }
  },
  beforeUnmount() {
    if (this.reservationsChartInstance) this.reservationsChartInstance.destroy();
    if (this.revenueByLotInstance) this.revenueByLotInstance.destroy();
    if (this.occupancyChartInstance) this.occupancyChartInstance.destroy();
  }
};

const UserChartsView = {
  template: `
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="card chart-card">
            <div class="card-body">
              <h5 class="mb-3">Daily Usage (7 days)</h5>
              <canvas ref="usageChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card chart-card">
            <div class="card-body">
              <h5 class="mb-3">Lot Distribution</h5>
              <canvas ref="lotChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-12">
          <div class="card chart-card">
            <div class="card-body">
              <h5 class="mb-3">Status Breakdown</h5>
              <canvas ref="statusChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  props: ['chartData'],
  mounted() {
    this.renderCharts();
  },
  watch: {
    chartData: { deep: true, handler() { this.renderCharts(); } }
  },
  methods: {
    renderCharts() {
      this.$nextTick(() => {
        this.renderUsageChart();
        this.renderLotChart();
        this.renderStatusChart();
      });
    },
    renderUsageChart() {
      const ctx = this.$refs.usageChart;
      if (!ctx) return;
      if (this.usageChartInstance) this.usageChartInstance.destroy();
      const data = this.chartData.daily_usage || [];
      this.usageChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.map(d => d.date),
          datasets: [{
            label: 'Reservations',
            data: data.map(d => d.count),
            borderColor: '#0ea5e9',
            backgroundColor: 'rgba(14, 165, 233, 0.2)',
            tension: 0.2
          }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
      });
    },
    renderLotChart() {
      const ctx = this.$refs.lotChart;
      if (!ctx) return;
      if (this.lotChartInstance) this.lotChartInstance.destroy();
      const data = this.chartData.lot_distribution || [];
      this.lotChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.map(d => d.lot),
          datasets: [{
            data: data.map(d => d.count),
            backgroundColor: ['#22c55e', '#14b8a6', '#a855f7', '#f97316', '#3b82f6', '#ef4444']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
      });
    },
    renderStatusChart() {
      const ctx = this.$refs.statusChart;
      if (!ctx) return;
      if (this.statusChartInstance) this.statusChartInstance.destroy();
      const data = this.chartData.status_breakdown || [];
      this.statusChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(d => d.label),
          datasets: [{
            label: 'Reservations',
            data: data.map(d => d.count),
            backgroundColor: ['#22c55e', '#6366f1']
          }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
      });
    }
  },
  beforeUnmount() {
    if (this.usageChartInstance) this.usageChartInstance.destroy();
    if (this.lotChartInstance) this.lotChartInstance.destroy();
    if (this.statusChartInstance) this.statusChartInstance.destroy();
  }
};

// Main App
const App = {
  data() {
    return {
      currentView: 'login',
      user: null,
      token: null
    };
  },
  mounted() {
    this.token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    if (this.token && userStr) {
      this.user = JSON.parse(userStr);
      this.currentView = this.user.role === 'admin' ? 'admin' : 'user';
    }
  },
  methods: {
    handleLogin(user, token) {
      this.user = user;
      this.token = token;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      this.currentView = user.role === 'admin' ? 'admin' : 'user';
    },
    handleLogout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this.currentView = 'login';
    }
  },
  template: `
    <div>
      <Login v-if="currentView === 'login'" @login="handleLogin" />
      <AdminDashboard v-if="currentView === 'admin'" @logout="handleLogout" />
      <UserDashboard v-if="currentView === 'user'" @logout="handleLogout" />
    </div>
  `
};

// Create and mount app
try {
  console.log('Initializing Vue app...');
  const app = createApp(App);
  app.component('Login', Login);
  app.component('AdminDashboard', AdminDashboard);
  app.component('UserDashboard', UserDashboard);
  app.component('ChartsView', ChartsView);
  app.component('UserChartsView', UserChartsView);
  app.mount('#app');
  console.log('Vue app mounted successfully!');
} catch (error) {
  console.error('Error mounting Vue app:', error);
  document.getElementById('app').innerHTML = `
    <div class="container mt-5">
      <div class="alert alert-danger">
        <h4>Application Error</h4>
        <p>Failed to initialize the application.</p>
        <pre>${error.message}</pre>
        <p>Please check the browser console for more details.</p>
      </div>
    </div>
  `;
}
