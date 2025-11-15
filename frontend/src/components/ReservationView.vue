<!--
Reservation View Component
Displays detailed reservation information
-->

<template>
  <div class="container mt-4">
    <h2>Reservation Details</h2>
    <div v-if="reservation" class="card">
      <div class="card-body">
        <h5 class="card-title">Reservation #{{ reservation.id }}</h5>
        <table class="table">
          <tbody>
            <tr>
              <th>Spot Number:</th>
              <td>{{ reservation.spot_number }}</td>
            </tr>
            <tr>
              <th>Parking Lot:</th>
              <td>{{ reservation.lot_name }}</td>
            </tr>
            <tr>
              <th>Start Time:</th>
              <td>{{ formatDate(reservation.start_time) }}</td>
            </tr>
            <tr>
              <th>End Time:</th>
              <td>{{ formatDate(reservation.end_time) || 'Active' }}</td>
            </tr>
            <tr>
              <th>Cost:</th>
              <td>{{ reservation.cost ? '$' + reservation.cost : 'Pending' }}</td>
            </tr>
            <tr>
              <th>Status:</th>
              <td>
                <span class="badge" :class="reservation.status === 'active' ? 'bg-success' : 'bg-secondary'">
                  {{ reservation.status }}
                </span>
              </td>
            </tr>
            <tr>
              <th>Created At:</th>
              <td>{{ formatDate(reservation.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="alert alert-info">
      No reservation selected
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReservationView',
  props: {
    reservation: {
      type: Object,
      default: null
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString();
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

