<!--
Parking Lot View Component
Displays all parking lots with their availability status
-->

<template>
  <div class="container mt-4">
    <h2>Parking Lots</h2>
    <div class="row">
      <div class="col-md-6 mb-4" v-for="lot in parkingLots" :key="lot.id">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h4>{{ lot.name }}</h4>
          </div>
          <div class="card-body">
            <p><strong>Address:</strong> {{ lot.address }}</p>
            <p><strong>Price per Hour:</strong> ${{ lot.price }}</p>
            <div class="mb-2">
              <strong>Availability:</strong>
              <div class="progress mt-2">
                <div 
                  class="progress-bar bg-success" 
                  :style="{ width: (lot.available_spots / lot.number_of_spots * 100) + '%' }"
                >
                  {{ lot.available_spots }} Available
                </div>
                <div 
                  class="progress-bar bg-warning" 
                  :style="{ width: (lot.occupied_spots / lot.number_of_spots * 100) + '%' }"
                >
                  {{ lot.occupied_spots }} Occupied
                </div>
              </div>
            </div>
            <p class="text-muted">
              Total Spots: {{ lot.number_of_spots }} | 
              Available: <span class="text-success">{{ lot.available_spots }}</span> | 
              Occupied: <span class="text-warning">{{ lot.occupied_spots }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParkingLotView',
  props: {
    parkingLots: {
      type: Array,
      default: () => []
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

