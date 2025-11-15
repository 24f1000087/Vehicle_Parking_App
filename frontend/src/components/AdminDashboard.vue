<!--
Admin Dashboard Component
Admin-only dashboard for managing parking lots, users, and viewing statistics
-->

<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Admin Dashboard</h2>
      <button class="btn btn-secondary" @click="handleLogout">Logout</button>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <h5 class="card-title">Total Lots</h5>
            <h2>{{ summary.total_lots || 0 }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Available Spots</h5>
            <h2>{{ summary.available_spots || 0 }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <h5 class="card-title">Occupied Spots</h5>
            <h2>{{ summary.occupied_spots || 0 }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Total Revenue</h5>
            <h2>${{ summary.total_revenue || 0 }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'lots' }" @click="activeTab = 'lots'" href="#">Parking Lots</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'" href="#">Users</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'charts' }" @click="activeTab = 'charts'" href="#">Charts</a>
      </li>
    </ul>

    <!-- Parking Lots Tab -->
    <div v-if="activeTab === 'lots'">
      <div class="d-flex justify-content-between mb-3">
        <h4>Manage Parking Lots</h4>
        <button class="btn btn-primary" @click="showAddModal = true">Add New Lot</button>
      </div>

      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Address</th>
              <th>Price/Hour</th>
              <th>Total Spots</th>
              <th>Available</th>
              <th>Occupied</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lot in parkingLots" :key="lot.id">
              <td>{{ lot.id }}</td>
              <td>{{ lot.name }}</td>
              <td>{{ lot.address }}</td>
              <td>${{ lot.price }}</td>
              <td>{{ lot.number_of_spots }}</td>
              <td><span class="badge bg-success">{{ lot.available_spots }}</span></td>
              <td><span class="badge bg-warning">{{ lot.occupied_spots }}</span></td>
              <td>
                <button class="btn btn-sm btn-info" @click="viewSpots(lot.id)">View Spots</button>
                <button class="btn btn-sm btn-warning" @click="editLot(lot)">Edit</button>
                <button class="btn btn-sm btn-danger" @click="deleteLot(lot.id)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'">
      <h4>All Users</h4>
      <div class="table-responsive">
        <table class="table table-striped">
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
              <td><span class="badge" :class="user.role === 'admin' ? 'bg-danger' : 'bg-primary'">{{ user.role }}</span></td>
              <td>{{ formatDate(user.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Charts Tab -->
    <div v-if="activeTab === 'charts'">
      <ChartsView :chartData="chartData" />
    </div>

    <!-- Add/Edit Lot Modal -->
    <div class="modal" :class="{ show: showAddModal || showEditModal }" style="display: block" v-if="showAddModal || showEditModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ showEditModal ? 'Edit Parking Lot' : 'Add Parking Lot' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveLot">
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" v-model="lotForm.name" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <input type="text" class="form-control" v-model="lotForm.address" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Price per Hour ($)</label>
                <input type="number" step="0.01" class="form-control" v-model="lotForm.price" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots</label>
                <input type="number" class="form-control" v-model="lotForm.number_of_spots" required :disabled="showEditModal" />
              </div>
              <button type="submit" class="btn btn-primary">Save</button>
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Spots Modal -->
    <div class="modal" :class="{ show: showSpotsModal }" style="display: block" v-if="showSpotsModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Parking Spots</h5>
            <button type="button" class="btn-close" @click="showSpotsModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-3 mb-2" v-for="spot in spots" :key="spot.id">
                <div class="card" :class="spot.status === 'A' ? 'bg-success' : 'bg-warning'">
                  <div class="card-body text-center text-white">
                    <strong>{{ spot.spot_number }}</strong>
                    <br />
                    <small>{{ spot.status === 'A' ? 'Available' : 'Occupied' }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ChartsView from './ChartsView.vue';

const API_BASE_URL = 'http://localhost:5000/api';

export default {
  name: 'AdminDashboard',
  components: {
    ChartsView
  },
  data() {
    return {
      activeTab: 'lots',
      parkingLots: [],
      users: [],
      summary: {},
      chartData: {},
      showAddModal: false,
      showEditModal: false,
      showSpotsModal: false,
      spots: [],
      lotForm: {
        name: '',
        address: '',
        price: '',
        number_of_spots: ''
      },
      editingLotId: null,
      error: ''
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    getAuthHeaders() {
      return {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      };
    },
    async loadData() {
      await Promise.all([
        this.loadSummary(),
        this.loadParkingLots(),
        this.loadUsers(),
        this.loadChartData()
      ]);
    },
    async loadSummary() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/summary`, this.getAuthHeaders());
        this.summary = response.data.summary;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load summary';
      }
    },
    async loadParkingLots() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/parking-lots`, this.getAuthHeaders());
        this.parkingLots = response.data.parking_lots;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load parking lots';
      }
    },
    async loadUsers() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/users`, this.getAuthHeaders());
        this.users = response.data.users;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load users';
      }
    },
    async loadChartData() {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/charts`, this.getAuthHeaders());
        this.chartData = response.data;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load chart data';
      }
    },
    async saveLot() {
      try {
        if (this.showEditModal) {
          await axios.put(
            `${API_BASE_URL}/admin/parking-lots/${this.editingLotId}`,
            this.lotForm,
            this.getAuthHeaders()
          );
        } else {
          await axios.post(
            `${API_BASE_URL}/admin/parking-lots`,
            this.lotForm,
            this.getAuthHeaders()
          );
        }
        this.closeModal();
        this.loadParkingLots();
        this.loadSummary();
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to save parking lot';
      }
    },
    editLot(lot) {
      this.editingLotId = lot.id;
      this.lotForm = {
        name: lot.name,
        address: lot.address,
        price: lot.price,
        number_of_spots: lot.number_of_spots
      };
      this.showEditModal = true;
    },
    async deleteLot(lotId) {
      if (!confirm('Are you sure you want to delete this parking lot?')) return;
      
      try {
        await axios.delete(`${API_BASE_URL}/admin/parking-lots/${lotId}`, this.getAuthHeaders());
        this.loadParkingLots();
        this.loadSummary();
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to delete parking lot';
      }
    },
    async viewSpots(lotId) {
      try {
        const response = await axios.get(`${API_BASE_URL}/admin/spots/${lotId}`, this.getAuthHeaders());
        this.spots = response.data.spots;
        this.showSpotsModal = true;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load spots';
      }
    },
    closeModal() {
      this.showAddModal = false;
      this.showEditModal = false;
      this.lotForm = {
        name: '',
        address: '',
        price: '',
        number_of_spots: ''
      };
      this.editingLotId = null;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString();
    },
    handleLogout() {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal.show {
  display: block !important;
}
</style>

