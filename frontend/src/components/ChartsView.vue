<!--
Charts View Component
Displays charts using Chart.js for data visualization
-->

<template>
  <div class="container-fluid mt-4">
    <h2>Analytics & Charts</h2>
    
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Daily Reservations (Last 7 Days)</h5>
          </div>
          <div class="card-body">
            <canvas ref="reservationsChart"></canvas>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Daily Revenue (Last 7 Days)</h5>
          </div>
          <div class="card-body">
            <canvas ref="revenueChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5>Lot Occupancy</h5>
          </div>
          <div class="card-body">
            <canvas ref="occupancyChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'ChartsView',
  props: {
    chartData: {
      type: Object,
      default: () => ({
        daily_reservations: [],
        daily_revenue: [],
        lot_occupancy: []
      })
    }
  },
  mounted() {
    this.renderCharts();
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        this.renderCharts();
      }
    }
  },
  methods: {
    renderCharts() {
      this.$nextTick(() => {
        this.renderReservationsChart();
        this.renderRevenueChart();
        this.renderOccupancyChart();
      });
    },
    renderReservationsChart() {
      const ctx = this.$refs.reservationsChart;
      if (!ctx) return;

      // Destroy existing chart if it exists
      if (this.reservationsChartInstance) {
        this.reservationsChartInstance.destroy();
      }

      const data = this.chartData.daily_reservations || [];
      this.reservationsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.map(d => d.date),
          datasets: [{
            label: 'Reservations',
            data: data.map(d => d.count),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    },
    renderRevenueChart() {
      const ctx = this.$refs.revenueChart;
      if (!ctx) return;

      if (this.revenueChartInstance) {
        this.revenueChartInstance.destroy();
      }

      const data = this.chartData.daily_revenue || [];
      this.revenueChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(d => d.date),
          datasets: [{
            label: 'Revenue ($)',
            data: data.map(d => d.revenue),
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    },
    renderOccupancyChart() {
      const ctx = this.$refs.occupancyChart;
      if (!ctx) return;

      if (this.occupancyChartInstance) {
        this.occupancyChartInstance.destroy();
      }

      const data = this.chartData.lot_occupancy || [];
      this.occupancyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(d => d.lot_name),
          datasets: [
            {
              label: 'Occupied',
              data: data.map(d => d.occupied),
              backgroundColor: 'rgba(255, 99, 132, 0.5)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1
            },
            {
              label: 'Available',
              data: data.map(d => d.available),
              backgroundColor: 'rgba(75, 192, 192, 0.5)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  },
  beforeUnmount() {
    if (this.reservationsChartInstance) {
      this.reservationsChartInstance.destroy();
    }
    if (this.revenueChartInstance) {
      this.revenueChartInstance.destroy();
    }
    if (this.occupancyChartInstance) {
      this.occupancyChartInstance.destroy();
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}
</style>

