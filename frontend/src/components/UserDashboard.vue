<!--
User Dashboard Component
User dashboard for booking spots, viewing reservations, and exporting data
-->

<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>User Dashboard</h2>
      <button class="btn btn-secondary" @click="handleLogout">Logout</button>
    </div>

    <!-- Active Reservation Alert -->
    <div v-if="activeReservation" class="alert alert-info">
      <h5>Active Reservation</h5>
      <p><strong>Spot:</strong> {{ activeReservation.spot_number }} at {{ activeReservation.lot_name }}</p>
      <p><strong>Started:</strong> {{ formatDate(activeReservation.start_time) }}</p>
      <button class="btn btn-danger" @click="vacateSpot">Vacate Spot</button>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'lots' }" @click="activeTab = 'lots'" href="#">Available Lots</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'reservations' }" @click="activeTab = 'reservations'" href="#">My Reservations</a>
      </li>
    </ul>

    <!-- Parking Lots Tab -->
    <div v-if="activeTab === 'lots'">
      <h4>Available Parking Lots</h4>
      <div class="row">
        <div class="col-md-6 mb-3" v-for="lot in parkingLots" :key="lot.id">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ lot.name }}</h5>
              <p class="card-text">
                <strong>Address:</strong> {{ lot.address }}<br />
                <strong>Price:</strong> ${{ lot.price }}/hour<br />
                <strong>Available Spots:</strong> 
                <span class="badge bg-success">{{ lot.available_spots }}</span> / 
                <span class="badge bg-secondary">{{ lot.number_of_spots }}</span>
              </p>
              <button 
                class="btn btn-primary" 
                @click="bookSpot(lot.id)"
                :disabled="lot.available_spots === 0 || activeReservation"
              >
                {{ lot.available_spots === 0 ? 'No Spots Available' : 'Book Spot' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reservations Tab -->
    <div v-if="activeTab === 'reservations'">
      <div class="d-flex justify-content-between mb-3">
        <h4>My Reservations</h4>
        <button class="btn btn-success" @click="exportCSV">Export CSV</button>
      </div>
      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Spot Number</th>
              <th>Lot Name</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Cost</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="reservation in reservations" :key="reservation.id">
              <td>{{ reservation.id }}</td>
              <td>{{ reservation.spot_number }}</td>
              <td>{{ reservation.lot_name }}</td>
              <td>{{ formatDate(reservation.start_time) }}</td>
              <td>{{ formatDate(reservation.end_time) || 'Active' }}</td>
              <td>{{ reservation.cost ? '$' + reservation.cost : 'Pending' }}</td>
              <td>
                <span class="badge" :class="reservation.status === 'active' ? 'bg-success' : 'bg-secondary'">
                  {{ reservation.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>

    <!-- Success Alert -->
    <div v-if="success" class="alert alert-success mt-3">
      {{ success }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default {
  name: 'UserDashboard',
  data() {
    return {
      activeTab: 'lots',
      parkingLots: [],
      reservations: [],
      activeReservation: null,
      error: '',
      success: ''
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
        this.loadParkingLots(),
        this.loadReservations(),
        this.loadActiveReservation()
      ]);
    },
    async loadParkingLots() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/parking-lots`, this.getAuthHeaders());
        this.parkingLots = response.data.parking_lots;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load parking lots';
      }
    },
    async loadReservations() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/reservations`, this.getAuthHeaders());
        this.reservations = response.data.reservations;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load reservations';
      }
    },
    async loadActiveReservation() {
      try {
        const response = await axios.get(`${API_BASE_URL}/user/reservations/active`, this.getAuthHeaders());
        this.activeReservation = response.data.reservation;
      } catch (err) {
        // No active reservation is fine
        this.activeReservation = null;
      }
    },
    async bookSpot(lotId) {
      if (this.activeReservation) {
        this.error = 'You already have an active reservation';
        return;
      }

      try {
        const response = await axios.post(
          `${API_BASE_URL}/user/book`,
          { lot_id: lotId },
          this.getAuthHeaders()
        );
        this.success = 'Spot booked successfully!';
        this.error = '';
        await this.loadData();
        setTimeout(() => {
          this.success = '';
        }, 3000);
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to book spot';
        this.success = '';
      }
    },
    async vacateSpot() {
      if (!confirm('Are you sure you want to vacate this spot?')) return;

      try {
        const response = await axios.post(
          `${API_BASE_URL}/user/vacate`,
          {},
          this.getAuthHeaders()
        );
        this.success = `Spot vacated! Total cost: $${response.data.reservation.cost}`;
        this.error = '';
        await this.loadData();
        setTimeout(() => {
          this.success = '';
        }, 5000);
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to vacate spot';
        this.success = '';
      }
    },
    async exportCSV() {
      try {
        // Use synchronous export for immediate download
        const response = await axios.get(
          `${API_BASE_URL}/user/export-csv-sync`,
          {
            ...this.getAuthHeaders(),
            responseType: 'blob'
          }
        );
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `reservations_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        this.success = 'CSV exported successfully!';
        setTimeout(() => {
          this.success = '';
        }, 3000);
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to export CSV';
      }
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
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

