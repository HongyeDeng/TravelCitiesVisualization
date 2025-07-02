<template>
  <div class="journey-designer-container" @click="handlePageClick" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <!-- Intro Title Section -->
    <transition name="intro-fade-slide">
      <div v-if="showIntro" :class="['intro-title-overlay', { 'intro-moved': introMoved }]">
        <a-typography-title :level="1" class="intro-main-title">Design Your Journey</a-typography-title>
      </div>
    </transition>

    <!-- Main Content (Hidden initially, appears after intro) -->
    <transition name="main-content-fade">
      <div v-if="!showIntro" class="main-journey-content">
        <a-row :gutter="[24, 24]" class="journey-content-row">
          <!-- Left Half: Journey Route Display (1/2 width) -->
          <a-col :xs="24" :md="12" class="journey-column">
            <a-card title="Your Journey Route" class="journey-card">
              <div class="journey-list-wrapper">
                <transition-group name="journey-item" tag="div" class="journey-list">
                  <div v-for="(city, index) in journeyCities" :key="city.id" class="journey-item">
                    <span class="item-index">{{ index + 1 }}.</span>
                    <span class="item-name">{{ city.city }}, {{ city.country }}</span>
                    <a-button type="text" danger size="small" @click="removeCityFromJourney(city.id)" class="remove-button">
                      <CloseOutlined />
                    </a-button>
                  </div>
                </transition-group>
                <a-empty v-if="journeyCities.length === 0" description="Double-click cities on the map to add them to your journey." class="empty-journey" />
              </div>
              <div class="confirm-button-wrapper">
                <a-button type="primary" size="large" :disabled="journeyCities.length === 0" @click="confirmJourney">
                  Confirm Journey
                </a-button>
              </div>
            </a-card>
          </a-col>

          <!-- Right Half: Leaflet Map (1/2 width) -->
          <a-col :xs="24" :md="12" class="map-column-journey">
            <a-card title="Select Cities on Map" class="map-card" :loading="loadingCitiesData">
              <div id="journey-map" class="map-element"></div>
              <a-spin v-if="loadingCitiesData" size="large" tip="Loading cities..." class="map-spinner-overlay" />
            </a-card>
          </a-col>
        </a-row>
      </div>
    </transition>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue';
import { Card, Row, Col, Button, Empty, message, Spin, Typography } from 'ant-design-vue';
import { CloseOutlined } from '@ant-design/icons-vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useJourneyStore } from '../stores/journey';

const API_BASE_URL = 'http://localhost:5000';

export default defineComponent({
  name: 'JourneyDesigner',
  components: {
    'a-card': Card,
    'a-row': Row,
    'a-col': Col,
    'a-button': Button,
    'a-empty': Empty,
    'a-spin': Spin,
    'a-typography-title': Typography.Title,
    CloseOutlined,
  },
  setup() {
    const journeyStore = useJourneyStore();
    
    const allCitiesData = ref([]);
    const loadingCitiesData = ref(false);

    let map = null;
    let circleMarkersLayer = null;
    let journeyRoutePolyline = null;
    const cityMarkers = new Map();

    const journeyCities = computed(() => journeyStore.getJourneyCities);

    const showIntro = ref(true);
    const introMoved = ref(false); // introMoved is back!

    // Dynamic background image URL
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Ensure this path is correct

    /**
     * Handles the initial animation of the title.
     * This will make the title move up and shrink slightly.
     */
    const animateIntroTitle = () => {
      setTimeout(() => {
        introMoved.value = true; // Trigger movement and scaling after a short delay
      }, 500); // Adjust delay as needed
    };

    const handlePageClick = () => {
      // On click, the title fully fades out and main content fades in
      if (showIntro.value) {
        showIntro.value = false;
      }
    };

    const fetchAllCities = async () => {
      loadingCitiesData.value = false; // Set to true at the start of fetch
      try {
        const response = await fetch(`${API_BASE_URL}/search_cities?limit=9999`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allCitiesData.value = data.map(city => ({
            id: city.id,
            city: city.city,
            country: city.country,
            latitude: parseFloat(city.latitude),
            longitude: parseFloat(city.longitude),
            budget_level: city.budget_level, // Include budget_level
            culture: city.culture,           // Include all rating properties
            adventure: city.adventure,
            nature: city.nature,
            beaches: city.beaches,
            nightlife: city.nightlife,
            cuisine: city.cuisine,
            wellness: city.wellness,
            urban: city.urban,
            seclusion: city.seclusion,
            // ... ensure all properties required by JourneyCity interface are here
        }));
        updateMapPoints();
      } catch (error) {
        console.error('Error fetching all cities:', error);
        allCitiesData.value = [];
        message.error('Failed to load cities for the map.');
      } finally {
        loadingCitiesData.value = false;
      }
    };

    const initMap = () => {
      if (!map) {
        map = L.map('journey-map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        circleMarkersLayer = L.layerGroup().addTo(map);
        journeyRoutePolyline = L.polyline([], {
            color: '#ff7800',
            weight: 5,
            opacity: 0.7,
            dashArray: '10, 10',
            lineCap: 'round',
            lineJoin: 'round'
        }).addTo(map);
      }
      map.invalidateSize();
    };

    const getMarkerColor = (cityId) => {
        return journeyStore.getJourneyCityIds.includes(cityId) ? '#ff0000' : '#1890ff';
    };

    const updateMapPoints = () => {
      if (!map || !circleMarkersLayer) return;

      circleMarkersLayer.clearLayers();
      cityMarkers.clear();

      allCitiesData.value.forEach(city => {
        const lat = parseFloat(city.latitude);
        const lon = parseFloat(city.longitude);

        if (!isNaN(lat) && !isNaN(lon)) {
          const markerColor = getMarkerColor(city.id);
          const circleMarker = L.circleMarker([lat, lon], {
            radius: 8,
            fillColor: markerColor,
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
          }).bindPopup(`<b>${city.city}</b><br>${city.country}`);

          circleMarker.on('dblclick', () => {
            journeyStore.addCity(city);
            message.success(`Added ${city.city} to journey!`);
          });

          circleMarkersLayer.addLayer(circleMarker);
          cityMarkers.set(city.id, circleMarker);
        }
      });

      if (allCitiesData.value.length > 0) {
        const bounds = allCitiesData.value.map(city => [city.latitude, city.longitude]);
        map.flyToBounds(bounds, {
          padding: [20, 20],
          duration: 1.0
        });
      } else {
        map.setView([20, 0], 2);
      }
      drawJourneyRoute();
    };

    const drawJourneyRoute = () => {
        if (journeyRoutePolyline) {
            journeyRoutePolyline.setLatLngs(journeyStore.getJourneyCoordinates);
        }

        allCitiesData.value.forEach(city => {
            const marker = cityMarkers.get(city.id);
            if (marker) {
                marker.setStyle({ fillColor: getMarkerColor(city.id) });
            }
        });
    };

    const removeCityFromJourney = (cityId) => {
      journeyStore.removeCity(cityId);
      message.info('City removed from journey.');
    };

    const confirmJourney = () => {
      const confirmedCityNames = journeyStore.confirmJourneyRoute();
      message.success(`Journey confirmed with ${confirmedCityNames.length} cities!`);
      console.log("Confirmed Journey:", confirmedCityNames);
    };

    onMounted(() => {
      animateIntroTitle(); // Call the animation on mount
    });

    onBeforeUnmount(() => {
      if (map) {
        map.remove();
        map = null;
      }
    });

    watch(showIntro, (newValue) => {
      if (!newValue) {
        nextTick(() => {
          initMap();
          fetchAllCities();
        });
      }
    });

    watch(journeyCities, () => {
        drawJourneyRoute();
    }, { deep: true });

    return {
      showIntro,
      introMoved, // Expose introMoved again
      handlePageClick,
      journeyCities,
      loadingCitiesData,
      removeCityFromJourney,
      confirmJourney,
      backgroundImageUrl
    };
  }
});
</script>

<style scoped>
.journey-designer-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden;
  position: relative;
  
  /* Background image set via inline style in template */
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

/* Intro Title Overlay */
.intro-title-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-width: 1200px;
  text-align: center;
  z-index: 100;
  transition: all 1.5s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* Transition for initial movement/scale */
  pointer-events: none; /* Allows clicks to pass through to the container */
}

.intro-moved {
  top: 5%; /* Move to top */
  transform: translate(-50%, 0) scale(0.7); /* Scale down to 70% */
  opacity: 0.7; /* Slightly fade out */
  /* transition property is on the .intro-title-overlay itself */
}

.intro-main-title {
  font-size: 6.5em; /* Made initial font size significantly bigger */
  color: #1890ff; /* Set to Ant Design blue for the initial title */
  text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.6);
  margin: 0;
  transition: font-size 1.5s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* Animate font size as well */
}

/* Intro Fade Out Animation (on click) */
.intro-fade-slide-leave-active {
  transition: opacity 1s ease-out; /* Pure fade out transition (on v-if change) */
}
.intro-fade-slide-leave-to {
  opacity: 0;
}

/* Main Content Fade In Animation */
.main-content-fade-enter-active {
  transition: opacity 1.5s ease-in 0.5s;
}
.main-content-fade-enter-from {
  opacity: 0;
}

/* Main Journey Content Styling (when intro is gone) */
.main-journey-content {
  width: 100%;
  height: 100%;
  opacity: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;

  /* Frosted glass effect */
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
}


.journey-content-row {
  width: 100%;
  height: 90%;
  max-width: 1800px;
  border-radius: 8px;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
}

.journey-column, .map-column-journey {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.journey-column {
  flex: 1;
  padding-right: 12px;
}

.map-column-journey {
  flex: 1;
  padding-left: 12px;
  position: relative;
}

.journey-card, .map-card {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  background-color: transparent;
}

/* Reset Ant Design card body padding to integrate better with frosted glass */
.ant-card :deep(.ant-card-body) {
  flex-grow: 1;
  height: auto;
  display: flex;
  flex-direction: column;
  padding: 24px;
}

/* Reset Ant Design card head padding/background */
.ant-card :deep(.ant-card-head) {
  background-color: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}
.ant-card :deep(.ant-card-head-title) {
  color: #333;
}


.journey-list-wrapper {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 24px;
  background-color: rgba(255, 255, 255, 0.1);
}

.journey-list {
  display: flex;
  flex-direction: column;
  height: 400px;
}

.journey-item {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  padding: 10px 15px;
  margin-bottom: 10px;
  font-size: 1.1em;
  font-weight: 500;
  color: #333;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
  position: relative;
}

.journey-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.6);
}

.item-index {
  margin-right: 10px;
  font-weight: bold;
  color: #1890ff;
}

.item-name {
  flex-grow: 1;
}

.remove-button {
  margin-left: 10px;
  font-size: 16px;
  color: #ff4d4f;
  transition: color 0.3s ease;
}

.remove-button:hover {
  color: #d9363e;
}

.confirm-button-wrapper {
  text-align: center;
  margin-top: auto;
  padding-top: 16px;
}

.empty-journey {
  padding: 40px;
  font-size: 1.1em;
  color: rgba(0, 0, 0, 0.45);
}

/* Vue Transition Group Animations */
.journey-item-enter-active, .journey-item-leave-active {
  transition: all 0.5s ease;
}
.journey-item-enter-from, .journey-item-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
.journey-item-move {
  transition: transform 0.5s ease;
}


.map-element {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background-color: #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.map-spinner-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .journey-designer-container {
    padding: 16px;
    height: auto;
    min-height: 100vh;
  }
  .journey-content-row {
    flex-direction: column;
    height: auto;
    padding: 16px;
  }
  .journey-column, .map-column-journey {
    padding: 0;
    margin-bottom: 24px;
    height: auto;
    flex: none;
  }
  .map-column-journey {
    margin-bottom: 0;
  }
  .map-element {
    height: 350px;
  }
  .ant-card :deep(.ant-card-body) {
    padding: 16px;
  }
}
</style>
