<template>
  <div class="analytics-dashboard-container" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <a-row :gutter="[24, 24]" class="dashboard-content-row">
      <!-- Left Half: Cities by Region Pie Chart -->
      <a-col :xs="24" :md="12" class="chart-column">
        <a-card :loading="loadingRegions" title="Cities by Region">
          <v-chart class="chart" :option="regionChartOption" @click="handleRegionChartClick" />
          <a-empty v-if="!loadingRegions && regionData.length === 0" description="No region data available." />
        </a-card>
      </a-col>

      <!-- Right Half: Cities by Country (in selected Region) Pie Chart -->
      <a-col :xs="24" :md="12" class="chart-column">
        <a-card :loading="loadingCountries" :title="countryChartTitle">
          <v-chart class="chart" :option="countryChartOption" />
          <a-empty v-if="!loadingCountries && countryData.length === 0" description="No country data available for selected region." />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { Card, Row, Col, Empty } from 'ant-design-vue';
import VChart from 'vue-echarts'; // ECharts component for Vue
import { use } from 'echarts/core';
import { PieChart } from 'echarts/charts'; // Import PieChart
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'; // Import necessary components
import { CanvasRenderer } from 'echarts/renderers';

// Register ECharts components
use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
]);

const API_BASE_URL = 'http://localhost:5000'; // Ensure this matches your Flask backend's address

export default defineComponent({
  name: 'AnalyticsDashboard',
  components: {
    'a-card': Card,
    'a-row': Row,
    'a-col': Col,
    'a-empty': Empty,
    VChart, // Register the ECharts component
  },
  setup() {
    const regionData = ref([]);
    const countryData = ref([]);
    const selectedRegion = ref(null); // Stores the region clicked on the left chart
    const loadingRegions = ref(false);
    const loadingCountries = ref(false);

    // Dynamic background image URL for AnalyticsDashboard
    // This assumes the same background image as App.vue and JourneyDesigner.vue
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Adjust this path if different

    // --- Chart Options for Regions ---
    const regionChartOption = computed(() => {
      if (regionData.value.length === 0 && !loadingRegions.value) {
        return {}; // Return empty option if no data and not loading
      }
      return {
        title: {
          text: 'Cities by Region',
          left: 'center',
          textStyle: { // Adjust title color for better visibility on frosted glass
            color: '#333'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: regionData.value.map(item => item.name),
          textStyle: { // Adjust legend text color
            color: '#333'
          }
        },
        series: [
          {
            name: 'Regions',
            type: 'pie',
            radius: ['40%', '70%'], // Doughnut chart effect
            center: ['50%', '60%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 20,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: regionData.value,
            animationType: 'scale', // Add animation
            animationEasing: 'elasticOut',
            animationDelay: function (idx) {
              return Math.random() * 200;
            }
          }
        ]
      };
    });

    // --- Chart Options for Countries ---
    const countryChartOption = computed(() => {
      if (countryData.value.length === 0 && !loadingCountries.value) {
        return {}; // Return empty option if no data and not loading
      }
      return {
        title: {
          text: selectedRegion.value ? `Cities in ${selectedRegion.value}` : 'Cities by Country',
          left: 'center',
          textStyle: { // Adjust title color for better visibility
            color: '#333'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: countryData.value.map(item => item.name),
          textStyle: { // Adjust legend text color
            color: '#333'
          }
        },
        series: [
          {
            name: 'Countries',
            type: 'pie',
            radius: ['40%', '70%'], // Doughnut chart effect
            center: ['50%', '60%'],
            roseType: 'area', // Nightingale Rose chart effect
            itemStyle: {
              borderRadius: 5
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 20,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: countryData.value,
            animationType: 'scale', // Add animation
            animationEasing: 'elasticOut',
            animationDelay: function (idx) {
              return Math.random() * 200;
            }
          }
        ]
      };
    });

    const countryChartTitle = computed(() => {
      return selectedRegion.value ? `Cities in ${selectedRegion.value}` : 'Cities by Country';
    });

    /**
     * Fetches city counts by region.
     */
    const fetchRegionData = async () => {
      loadingRegions.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/city_counts_by_region`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        regionData.value = data;
        // Optionally set an initial selected region if data exists
        if (data.length > 0) {
          selectedRegion.value = data[0].name;
        }
      } catch (error) {
        console.error('Error fetching region data:', error);
        regionData.value = [];
      } finally {
        loadingRegions.value = false;
      }
    };

    /**
     * Fetches city counts by country for the selected region.
     * @param {string} region - The region to fetch data for.
     */
    const fetchCountryData = async (region) => {
      if (!region) {
        countryData.value = [];
        return;
      }
      loadingCountries.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/city_counts_by_country_in_region?region=${encodeURIComponent(region)}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        countryData.value = data;
      } catch (error) {
        console.error(`Error fetching country data for ${region}:`, error);
        countryData.value = [];
      } finally {
        loadingCountries.value = false;
      }
    };

    /**
     * Handles click events on the region pie chart.
     * @param {object} params - ECharts click event parameters.
     */
    const handleRegionChartClick = (params) => {
      if (params.componentType === 'series' && params.seriesType === 'pie') {
        selectedRegion.value = params.name; // Update selected region based on clicked slice
      }
    };

    // Lifecycle Hook: Component Mounted
    onMounted(() => {
      fetchRegionData(); // Fetch initial region data on mount
    });

    // Watcher: React to changes in selectedRegion to update country chart
    watch(selectedRegion, (newRegion) => {
      fetchCountryData(newRegion);
    }, { immediate: true }); // Fetch country data immediately for the initial selected region

    return {
      regionData,
      countryData,
      selectedRegion,
      loadingRegions,
      loadingCountries,
      regionChartOption,
      countryChartOption,
      countryChartTitle,
      handleRegionChartClick,
      backgroundImageUrl, // Expose the background image URL
    };
  }
});
</script>

<style scoped>
.analytics-dashboard-container {
  /* This container now acts as a transparent wrapper, allowing App.vue's background to show */
  width: 100vw;
  height: 100vh;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px; /* Padding for the container */
  box-sizing: border-box;
  
    /* Background image set via inline style in template */
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.dashboard-content-row {
  /* This is the main content panel with the frosted glass effect */
  width: 90%;
  height: 90%;
  max-width: 1800px;
  
  /* Frosted glass effect properties */
  background-color: rgba(255, 255, 255, 0.2); /* Semi-transparent white */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  -webkit-backdrop-filter: blur(10px); /* For Safari support */
  border-radius: 12px; /* Rounded corners */
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); /* Subtle shadow */
  border: 1px solid rgba(255, 255, 255, 0.18); /* Light border */
  
  padding: 24px; /* Padding inside the frosted glass panel */
  box-sizing: border-box;
  display: flex; /* Ensure flex layout for columns */
  flex-direction: row; /* Arrange columns horizontally */
}

.chart-column {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.ant-card {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  box-shadow: none; /* Remove default Ant Card shadow */
  background-color: transparent; /* Make card transparent to let frosted glass show through */
}

/* Adjust Ant Design card internal elements to be transparent/blend */
.ant-card :deep(.ant-card-head) {
  background-color: rgba(255, 255, 255, 0.1); /* Slightly visible header background */
  border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* Light border for header */
}
.ant-card :deep(.ant-card-head-title) {
  color: #333; /* Darker title for readability against light frosted glass */
}
.ant-card :deep(.ant-card-body) {
  flex-grow: 1;
  height: calc(100% - 56px); /* Adjust height for chart after card header (default 56px) */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: transparent; /* Ensure body itself is transparent */
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .analytics-dashboard-container {
    padding: 16px;
    height: auto;
    min-height: 100vh;
  }
  .dashboard-content-row {
    height: auto;
    padding: 16px;
    flex-direction: column; /* Stack columns vertically on small screens */
  }
  .chart-column {
    height: 400px;
    margin-bottom: 24px;
  }
  .chart-column:last-child {
    margin-bottom: 0;
  }
}
</style>
