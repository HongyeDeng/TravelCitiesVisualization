<template>
  <div class="city-detail-explorer-container" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <a-typography-title :level="2" class="page-title">Explore Detail of Cities</a-typography-title>
    <a-row :gutter="[24, 24]" class="main-content-row">
      <!-- Left Part: Map Visualization Controls (1/4 width) -->
      <a-col :xs="24" :md="6" class="control-column">
        <a-card title="Map Visualization" class="control-card">
          <p>Color map points by:</p>
          <a-space direction="vertical" :size="[0, 16]" class="control-buttons">
            <a-button
              v-for="prop in mapVizProperties"
              :key="prop.value"
              :type="activeVizProperty === prop.value ? 'primary' : 'default'"
              @click="activeVizProperty = prop.value"
              block
              size="large"
            >
              {{ prop.label }}
            </a-button>
          </a-space>
          <a-divider />
          <p>Click a city on the map to view details.</p>
        </a-card>
      </a-col>

      <!-- Middle Part: Selected City Details (1/4 width) -->
      <a-col :xs="24" :md="6" class="detail-column">
        <a-card :loading="!selectedCity" :title="selectedCity ? selectedCity.city : 'Select a City'" class="detail-card">
          <template v-if="selectedCity">
            <a-typography-title :level="5">{{ selectedCity.country }}</a-typography-title>
            <a-divider />

            <!-- Stacked Bar Plot for Ratings -->
            <div class="chart-wrapper">
              <v-chart class="chart" :option="stackedBarOption" autoresize />
            </div>

            <!-- Budget Level Text Box -->
            <div class="budget-box-wrapper">
              <div :class="['budget-box', budgetLevelClass(selectedCity.budget_level)]">
                <a-typography-text strong>Budget Level: {{ selectedCity.budget_level }}</a-typography-text>
              </div>
            </div>
          </template>
          <a-empty v-else description="No city selected yet. Click a point on the map." />
        </a-card>
      </a-col>

      <!-- Right Part: Leaflet Map (1/2 width) -->
      <a-col :xs="24" :md="12" class="map-column-right">
        <a-card title="City Map" class="map-card" :loading="loadingCitiesData">
          <div id="city-detail-map" class="map-element"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount, watch, computed } from 'vue';
import { Card, Row, Col, Typography, Space, Button, Divider, Empty } from 'ant-design-vue';
import L, {icon, Marker} from 'leaflet';
import 'leaflet/dist/leaflet.css';

// ECharts imports and registration for this component only
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  XAxisComponent,
  YAxisComponent
} from 'echarts/components';

// Register the necessary ECharts modules for this component
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  //XAxisComponent, // Included as it was commented out previously
  //YAxisComponent // Included as it was commented out previously
]);

var LeafIcon = L.Icon.extend({
    options: {
       iconSize:     [38, 95],
       shadowSize:   [50, 64],
       iconAnchor:   [22, 94],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76]
    }
});
var greenIcon = new LeafIcon({
    iconUrl: '/images/marker.svg',
})

const API_BASE_URL = 'http://localhost:5000'; // Your Flask backend URL

export default defineComponent({
  name: 'CityDetailExplorer',
  components: {
    'a-card': Card,
    'a-row': Row,
    'a-col': Col,
    'a-typography-title': Typography.Title,
    'a-space': Space,
    'a-button': Button,
    'a-divider': Divider,
    'a-empty': Empty,
    VChart, // ECharts component
  },
  setup() {
    const allCitiesData = ref([]); // Stores all cities fetched from backend
    const selectedCity = ref(null); // The city currently selected via map click
    const activeVizProperty = ref('budget_level'); // Default map visualization property
    const loadingCitiesData = ref(false); // Loading state for initial city data fetch

    let map = null; // Leaflet map instance
    let circleMarkersLayer = null; // Layer group for circle markers

    // Dynamic background image URL for CityDetailExplorer
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Adjust this path to your desired image

    // Properties available for map visualization and stacked bar chart
    const ratingProperties = [
      'culture', 'adventure', 'nature', 'beaches', 'nightlife',
      'cuisine', 'wellness', 'urban', 'seclusion'
    ];
    const mapVizProperties = [
      { label: 'Budget Level', value: 'budget_level' },
      { label: 'Culture Rating', value: 'culture' },
      { label: 'Adventure Rating', value: 'adventure' },
      { label: 'Nature Rating', value: 'nature' },
      { label: 'Beaches Rating', value: 'beaches' },
      { label: 'Nightlife Rating', value: 'nightlife' },
      { label: 'Cuisine Rating', value: 'cuisine' },
      { label: 'Wellness Rating', value: 'wellness' },
      { label: 'Urban Rating', value: 'urban' },
      { label: 'Seclusion Rating', value: 'seclusion' },
    ];

    /**
     * Helper function to get color for map circle markers based on property value.
     * For budget: specific colors. For ratings: a gradient.
     */
    const getColorForProperty = (city, property) => {
      if (!city || city[property] === undefined || city[property] === null) {
        return '#ccc'; // Default gray for missing data
      }

      if (property === 'budget_level') {
        switch (String(city.budget_level).toLowerCase()) { // Ensure it's a string before toLowerCase
          case 'luxury': return '#FFD700'; // Gold
          case 'mid-range': return '#1890ff'; // Ant Design Blue
          case 'budget': return '#52c41a'; // Ant Design Green
          default: return '#ccc';
        }
      } else if (ratingProperties.includes(property)) {
        // Interpolate color based on 0-5 rating
        const rating = parseInt(city[property]);
        if (isNaN(rating)) return '#ccc';
        
        // Simple 5-step gradient from light blue to dark blue (or green to red etc.)
        const colors = ['#808080', '#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c']; // Example colors
        return colors[Math.min(rating, 5)] || '#ccc'; // Clamp to 5, provide default
      }
      return '#ccc'; // Default color
    };

    /**
     * CSS class for budget level text box.
     */
    const budgetLevelClass = (level) => {
      if (!level) return '';
      switch (String(level).toLowerCase()) { // Ensure it's a string before toLowerCase
        case 'luxury': return 'budget-luxury';
        case 'mid-range': return 'budget-mid-range';
        case 'budget': return 'budget-budget';
        default: return '';
      }
    };

    /**
     * ECharts option for the stacked bar chart of the selected city's ratings.
     */
    const getRandomColor = () => {
        const hue = Math.floor(Math.random() * 360);
        return `hsl(${hue}, 70%, 60%)`;
    };
    const fixedGradientColors = [
        '#ff0000', // Red
        '#ff4000', // Orange Red
        '#ff8000', // Orange
        '#ffbf00', // Yellow Orange
        '#ffff00', // Yellow
        '#bfff80', // Light Yellow-Green
        '#80dfff', // Light Blue-Green
        '#66ccff', // Sky Blue
        '#add8e6'  // Light Blue
    ];
const stackedBarOption = computed(() => {
    if (!selectedCity.value) {
        return {};
    }

    const rawData = ratingProperties.map(prop => ({
        name: prop.charAt(0).toUpperCase() + prop.slice(1),
        value: selectedCity.value[prop] || 0
    }));

    // Sort by value descending
    const sorted = [...rawData].sort((a, b) => b.value - a.value);

    // Assign color based on sorted rank
    sorted.forEach((item, i) => {
        item.color = fixedGradientColors[i] || '#ccc'; // fallback if > 9
    });

    // Map back to original order (matching ratingProperties)
    const coloredData = rawData.map(item => {
        const match = sorted.find(s => s.name === item.name && s.value === item.value);
        return {
        name: item.name,
        value: item.value,
        color: match ? match.color : '#ccc'
        };
    });

    return {
        title: {
        text: `Ratings for ${selectedCity.value.city}`,
        left: 'center',
        show: true
        },
        tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: '{b}: {c}'
        },
        grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
        },
        xAxis: {
        type: 'value',
        boundaryGap: [0, 0.01],
        max: 5,
        interval: 1
        },
        yAxis: {
        type: 'category',
        data: coloredData.map(d => d.name),
        axisLabel: {
            color: 'black',
            formatter: value => value.replace('Rating', '').trim()
        }
        },
        series: [
        {
            name: 'Rating',
            type: 'bar',
            data: coloredData.map(d => ({
            value: d.value,
            itemStyle: {
                color: d.color,
                borderRadius: 4
            }
            })),
            showBackground: true,
            backgroundStyle: {
            color: 'rgba(180, 180, 180, 0.2)'
            }
        }
        ],
        animation: true,
        animationDuration: 1000
    };
    });


    /**
     * Fetches all city data from the backend.
     */
    const fetchAllCities = async () => {
      loadingCitiesData.value = false; // Set to true at the start of fetch
      try {
        // Fetch all cities (use a large limit if you have many cities)
        const response = await fetch(`${API_BASE_URL}/search_cities?limit=9999`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allCitiesData.value = data;
        if (data.length > 0) {
            selectedCity.value = data[0]; // Select the first city by default
        }
        updateMapPoints(); // Draw initial points on map
      } catch (error) {
        console.error('Error fetching all cities:', error);
        allCitiesData.value = [];
      } finally {
        loadingCitiesData.value = false;
      }
    };

    /**
     * Initializes the Leaflet map.
     */
    const initMap = () => {
      if (!map) {
        map = L.map('city-detail-map').setView([20, 0], 2); // Centered, low zoom
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        circleMarkersLayer = L.layerGroup().addTo(map);
      }
      map.invalidateSize(); // Important for proper map display
      if (map && map instanceof L.Map) {
        console.log('✅ Map initialized successfully (CityDetailExplorer)');
      } else {
        console.error('❌ Map initialization failed (CityDetailExplorer)');
      }   
    };

    /**
     * Updates city points on the map based on the active visualization property.
     */
    const updateMapPoints = () => {
      if (!map || !circleMarkersLayer) return;

      circleMarkersLayer.clearLayers(); // Clear existing markers

      const bounds = [];
      allCitiesData.value.forEach(city => {
        const lat = parseFloat(city.latitude);
        const lon = parseFloat(city.longitude);

        if (!isNaN(lat) && !isNaN(lon)) {
          const color = getColorForProperty(city, activeVizProperty.value);
          const circleMarker = L.circleMarker([lat, lon], {
            radius: 5,
            fillColor: color,
            color: 'transparent', // Border color
            weight: 0,
            opacity: 0.8,
            fillOpacity: 0.8
          }).bindPopup(`<b>${city.city}</b><br>${city.country}<br>Budget: ${city.budget_level || 'N/A'}`);

          circleMarker.on('click', () => {
            selectedCity.value = city; // Set clicked city as selected
            // Optionally, pan map to clicked city
            map.panTo([lat, lon]);
          });

          circleMarkersLayer.addLayer(circleMarker);
          bounds.push([lat, lon]);
        }
      });

      // Fit map to bounds of all cities, or default view if no cities
      if (bounds.length > 0) {
        map.flyToBounds(bounds, {
          padding: [20, 20],
          duration: 1.0
        });
      } else {
        map.setView([20, 0], 2);
      }
    };

    // Lifecycle hooks
    onMounted(() => {
      initMap(); // Initialize map when component is mounted
      fetchAllCities(); // Fetch all cities data
    });

    onBeforeUnmount(() => {
      if (map) {
        map.remove();
        map = null;
      }
    });

    // Watchers
    watch(activeVizProperty, () => {
      updateMapPoints(); // Redraw map points when visualization property changes
    });

    return {
      allCitiesData,
      selectedCity,
      activeVizProperty,
      loadingCitiesData,
      mapVizProperties,
      budgetLevelClass,
      stackedBarOption,
      backgroundImageUrl, // Expose the background image URL
    };
  }
});
</script>

<style scoped>
.city-detail-explorer-container {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden; /* Prevent scrollbars */
  position: relative;
  
  /* Background image properties - same as JourneyDesigner */
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  /* Remove background-color here as it will be covered by the image */
}

.page-title {
  text-align: center;
  margin-bottom: 24px;
  color: #fff; /* Changed to white for better contrast on background image */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); /* Stronger shadow for readability */
}

.main-content-row {
  width: 100%;
  flex-grow: 1;
  max-width: 1800px;
  /* Frosted glass effect for the main content panel - same as JourneyDesigner */
  background-color: rgba(255, 255, 255, 0.2); /* Semi-transparent white */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  -webkit-backdrop-filter: blur(10px); /* For Safari support */
  border-radius: 12px; /* Slight rounded corners */
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); /* Subtle shadow */
  border: 1px solid rgba(255, 255, 255, 0.18); /* Light border */
  
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
}

/* Common column styling for flex behavior */
.control-column,
.detail-column,
.map-column-right {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.detail-column {
    height: 800px;
}

/* Width distribution using flex-basis and flex-grow */
.control-column {
  flex: 1;
  padding-right: 12px;
}

.detail-column {
  flex: 1;
  padding: 0 12px;
}

.map-column-right {
  flex: 2;
  padding-left: 12px;
}

/* Card styling to fill column height */
.control-card,
.detail-card,
.map-card {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  box-shadow: none; /* Remove default shadow */
  display: flex;
  flex-direction: column;
  background-color: transparent; /* Make cards transparent to let frosted glass show */
}

/* Ensure card body takes remaining space */
.ant-card :deep(.ant-card-body) {
  flex-grow: 1;
  height: auto;
  display: flex;
  flex-direction: column;
  padding: 24px;
}

/* Adjust Ant Design card head padding/background for frosted glass */
.ant-card :deep(.ant-card-head) {
  background-color: rgba(255, 255, 255, 0.1); /* Slightly visible header background */
  border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* Light border for header */
}
.ant-card :deep(.ant-card-head-title) {
  color: #333; /* Darker title for readability against light frosted glass */
}


.control-buttons {
  width: 100%;
}

.control-buttons .ant-btn {
  width: 100%;
}

.chart-wrapper {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  width: 100%;
}

.chart {
  width: 100%;
  height: 100%;
}

.budget-box-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  width: 100%;
}

.budget-box {
  padding: 12px 20px;
  border-radius: 8px;
  text-align: center;
  font-size: 1.1em;
  font-weight: bold;
  color: white;
  transition: background-color 0.5s ease-in-out;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  animation: pulse 2s infinite ease-in-out;
}

/* Budget Level Specific Colors (no change here) */
.budget-luxury {
  background-color: #FFD700;
  color: #333;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}
.budget-mid-range {
  background-color: #1890ff;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}
.budget-budget {
  background-color: #52c41a;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}

/* Simple pulse animation (no change here) */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

.map-element {
  width: 100%;
  height: 100%;
  min-height: 600px;
  background-color: #e0e0e0; /* Placeholder background */
}

/* Responsive adjustments (no change here) */
@media (max-width: 768px) {
  .city-detail-explorer-container {
    padding: 16px;
    height: auto;
    min-height: 100vh;
  }
  .main-content-row {
    flex-direction: column;
    height: auto;
    padding: 16px;
  }
  .control-column,
  .detail-column,
  .map-column-right {
    padding: 0;
    margin-bottom: 24px;
    height: auto;
    flex: none;
  }
  .map-column-right {
    margin-bottom: 0;
  }
  .map-element {
    height: 350px;
  }
  .ant-card :deep(.ant-card-body) {
    padding: 16px;
  }
  .budget-box-wrapper {
    margin-top: 16px;
  }
}
</style>
