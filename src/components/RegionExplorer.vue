<template>
  <div class="region-explorer-container" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <a-row :gutter="[24, 24]" class="content-row">
      <!-- Left Half: Region Info and Navigation -->
      <a-col :xs="24" :md="10" class="info-column">
        <div class="info-card ant-card">
          <a-typography-title :level="2" class="region-title-wrapper">
            <transition name="fade-slide" mode="out-in">
              <span :key="currentRegionName">{{ currentRegionName || 'Loading...' }}</span>
            </transition>
          </a-typography-title>
          <a-typography-text class="cities-count-wrapper">
            <transition name="fade-slide" mode="out-in">
              <span :key="citiesCount">
                Cities: {{ loading ? '...' : citiesCount }}
              </span>
            </transition>
          </a-typography-text>

          <a-divider />

          <div class="navigation-buttons">
            <a-button type="primary" size="large" @click="prevRegion" :disabled="loading">
              Previous Region
            </a-button>
            <a-button type="primary" size="large" @click="nextRegion" :disabled="loading">
              Next Region
            </a-button>
          </div>

          <a-divider />

          <div class="city-list">
            <a-typography-title :level="4">Cities in {{ currentRegionName }}</a-typography-title>
            <a-list
              :loading="loading"
              :data-source="cities"
              :locale="{ emptyText: 'No cities found for this region.' }"
              class="scrollable-list"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta :title="item.city" :description="item.country" />
                </a-list-item>
              </template>
            </a-list>
          </div>
        </div>
      </a-col>

      <!-- Right Half: Leaflet Map -->
      <a-col :xs="24" :md="14" class="map-column">
        <div id="map-container" class="map-container">
          <a-spin v-if="loading" size="large" tip="Loading map data..." class="map-spinner" />
          <div id="map" class="map-element"></div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { Row, Col, Button, Typography, Divider, Spin, List } from 'ant-design-vue';
import L, {icon, Marker} from 'leaflet'; // Import Leaflet library
import 'leaflet/dist/leaflet.css'; // Import Leaflet CSS for map styling

var LeafIcon = L.Icon.extend({
    options: {
       iconSize:     [9, 25],
       shadowSize:   [50, 64],
       iconAnchor:   [11, 47],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76]
    }
});
var greenIcon = new LeafIcon({
    iconUrl: '/images/marker.svg',
})

var AsiaIcon = L.Icon.extend({
    options: {
       iconSize:     [18, 18],
       shadowSize:   [50, 64],
       iconAnchor:   [9, 9],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76],
       iconUrl: '/images/asia.png',
    }
});
var AfricaIcon = L.Icon.extend({
    options: {
       iconSize:     [18, 18],
       shadowSize:   [50, 64],
       iconAnchor:   [9, 9],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76],
       iconUrl: '/images/africa.png',
    }
});
var EuropeIcon = L.Icon.extend({
    options: {
       iconSize:     [18, 18],
       shadowSize:   [50, 64],
       iconAnchor:   [9, 9],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76],
       iconUrl: '/images/europe.png',
    }
});
var NorthAmericaIcon = L.Icon.extend({
    options: {
       iconSize:     [32, 32],
       shadowSize:   [50, 64],
       iconAnchor:   [9, 9],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76],
       iconUrl: '/images/north_america.png',
    }
});
var SouthAmericaIcon = L.Icon.extend({
    options: {
       iconSize:     [18, 18],
       shadowSize:   [50, 64],
       iconAnchor:   [9, 9],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76],
       iconUrl: '/images/south_america.png',
    }
});
var OceaniaIcon = L.Icon.extend({
    options: {
       iconSize:     [18, 18],
       shadowSize:   [50, 64],
       iconAnchor:   [9, 9],
       shadowAnchor: [4, 62],
       popupAnchor:  [-3, -76],
       iconUrl: '/images/oceania.png',
    }
});

// Backend Flask API URL
const API_BASE_URL = 'http://172.30.43.185:5000/'; // Make sure this matches your Flask backend's address

export default defineComponent({
  name: 'RegionExplorer',
  components: {
    'a-row': Row,
    'a-col': Col,
    'a-button': Button,
    'a-typography-title': Typography.Title,
    'a-typography-text': Typography.Text,
    'a-divider': Divider,
    'a-spin': Spin,
    'a-list': List,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
  },
  setup() {
    const currentRegionIndex = ref(0);
    const currentRegionName = ref(ALL_REGIONS[0]);
    const cities = ref([]);
    const citiesCount = ref(0);
    const loading = ref(false);
    let map = null; // Leaflet map instance
    let markersLayer = new L.LayerGroup(); // Layer group to easily clear and add markers

    // Dynamic background image URL for RegionExplorer
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Adjust this path to your desired image

    /**
     * Initializes the Leaflet map.
     * Called once when the component is mounted.
     */
    const initMap = () => {
      // Check if map already exists to prevent re-initialization
      if (map) {
        map.remove(); // Remove existing map instance
      }

      // Initialize the map on the 'map' div
      map = L.map('map').setView([0, 0], 2); // Default view, will be adjusted by fitBounds
      // Add OpenStreetMap tiles
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            minZoom: 0,
            maxZoom: 20,
            ext: 'png'
        }).addTo(map);
      
      // Add the markers layer to the map
      markersLayer.addTo(map);

      if (map && map instanceof L.Map) {
        console.log('✅ Map initialized successfully');
      } else {
        console.error('❌ Map initialization failed');
      }   
    };

    /**
     * Fetches city data for the given region from the Flask backend.
     * NOW USING THE /search_cities ENDPOINT as per user's correction.
     * @param {string} regionName - The name of the region to fetch cities for.
     */
    const fetchCitiesForRegion = async (regionName) => {
      loading.value = false; // Set to true at the start of fetch
      try {
        // Corrected endpoint from /recommend_cities to /search_cities
        const response = await fetch(`${API_BASE_URL}/search_cities?region=${encodeURIComponent(regionName)}&limit=1000`);
        console.log(`Fetching cities for region: ${regionName} from ${API_BASE_URL}/search_cities?region=${encodeURIComponent(regionName)}&limit=1000`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        cities.value = data;
        citiesCount.value = data.length;
        console.log(`Fetched ${citiesCount.value}`);
        
        updateMap(); // Update the map with new city data
      } catch (error) {
        console.error('Error fetching cities:', error);
        cities.value = [];
        citiesCount.value = 0;
        // Optionally display an error message using Ant Design Notification or Message
      } finally {
        loading.value = false;
      }
    };

    /**
     * Updates the Leaflet map with new markers based on the fetched cities.
     * Clears previous markers and adds new ones.
     */
    const updateMap = () => {
      if (!map) return;

      markersLayer.clearLayers(); // Clear all existing markers from the layer group
      
      const bounds = [];
      cities.value.forEach(city => {
        // Ensure latitude and longitude are valid numbers
        const lat = parseFloat(city.latitude);
        const lon = parseFloat(city.longitude);

        if (!isNaN(lat) && !isNaN(lon)) {
          let markerIcon; // Declare markerIcon here

          // Dynamically select icon based on city's region
          switch (city.region.toLowerCase()) {
            // case 'asia':
            //   markerIcon = new AsiaIcon();
            //   break;
            // case 'africa':
            //   markerIcon = new AfricaIcon();
            //   break;
            // case 'europe':
            //   markerIcon = new EuropeIcon();
            //   break;
            // case 'north_america': // Match the region string from data
            //   markerIcon = new NorthAmericaIcon();
            //   break;
            // case 'south_america': // Match the region string from data
            //   markerIcon = new SouthAmericaIcon();
            //   break;
            // case 'oceania':
            //   markerIcon = new OceaniaIcon();
            //   break;
            default:
              markerIcon = greenIcon; // Fallback to default green icon
          }

          const marker = L.marker([lat, lon], {icon: markerIcon}).bindPopup(`<b>${city.city}</b><br>${city.country}<br>Region: ${city.region}`); // City as a tag/popup
          marker.on('click', () => {
            map.flyTo([lat, lon], 13, { // Fly to the marker's coordinates with zoom level 13
              duration: 1.0 // Animation duration
            });
          });
          markersLayer.addLayer(marker); // Add marker to the layer group
          bounds.push([lat, lon]);
        } else {
            console.warn(`Invalid coordinates for city: ${city.city}, Lat: ${city.latitude}, Lon: ${city.longitude}`);
        }
      });

      // Fit map to markers with animation if there are cities
      if (bounds.length > 0) {
        map.flyToBounds(bounds, {
          padding: [50, 50], // Padding around the bounds
          duration: 1.5,     // Animation duration in seconds
          easeLinearity: 0.5 // Easing function
        });
      } else {
        // If no cities, reset map view or show a default location
        map.flyTo([0, 0], 2, { duration: 1.5 });
      }
    };

    /**
     * Navigates to the next region in the ALL_REGIONS array.
     */
    const nextRegion = () => {
      currentRegionIndex.value = (currentRegionIndex.value + 1) % ALL_REGIONS.length;
      currentRegionName.value = ALL_REGIONS[currentRegionIndex.value];
    };

    /**
     * Navigates to the previous region in the ALL_REGIONS array.
     */
    const prevRegion = () => {
      currentRegionIndex.value = (currentRegionIndex.value - 1 + ALL_REGIONS.length) % ALL_REGIONS.length;
      currentRegionName.value = ALL_REGIONS[currentRegionIndex.value];
    };

    // Lifecycle Hook: Component Mounted
    onMounted(() => {
      initMap(); // Initialize the map when the component is mounted
      fetchCitiesForRegion(currentRegionName.value); // Fetch initial region data
    });

    // Lifecycle Hook: Component Before Unmount (cleanup)
    onBeforeUnmount(() => {
      if (map) {
        map.remove(); // Destroy the map instance to prevent memory leaks
        map = null;
      }
    });

    // Watcher: React to changes in currentRegionName
    watch(currentRegionName, (newRegionName) => {
      if (newRegionName) {
        fetchCitiesForRegion(newRegionName);
      }
    });

    return {
      currentRegionName,
      cities,
      citiesCount,
      loading,
      nextRegion,
      prevRegion,
      backgroundImageUrl, // Expose the background image URL
    };
  }
});

// This is a simple list of regions for demonstration.
const ALL_REGIONS = [
  "North_America",
  "Europe",
  "Asia",
  "South_America",
  "Africa",
  "Oceania"
];
</script>

<style scoped>
.region-explorer-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px; /* Maintain padding if desired */
  box-sizing: border-box;
  overflow: hidden; /* Prevent scrollbars on the container itself */
  position: relative;
  
  /* Background image properties */
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed; /* Ensures the background image stays fixed as content scrolls */
  /* Remove background-color here as it will be covered by the image */
}

.content-row {
  width: 90%; /* Main content panel width */
  height: 90%; /* Main content panel height */
  max-width: 1400px; /* Still useful for larger screens */
  max-height: none; /* No max height, let it fill 90% */
  
  /* Frosted glass effect for the main content panel */
  background-color: rgba(255, 255, 255, 0.2); /* Semi-transparent white */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  -webkit-backdrop-filter: blur(10px); /* For Safari support */
  border-radius: 12px; /* Slight rounded corners */
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); /* Subtle shadow */
  border: 1px solid rgba(255, 255, 255, 0.18); /* Light border */
  
  padding: 24px; /* Standard padding inside the frosted glass panel */
  box-sizing: border-box;
  display: flex; /* Flex container for left and right columns */
  flex-direction: row;
}

.info-column {
  padding-right: 24px; /* Space between info and map columns */
}

.info-card {
  height: 100%; /* Fill available height */
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3); /* Lighter border for frosted look */
  border-radius: 8px;
  background-color: transparent; /* Make card transparent */
  box-shadow: none; /* Remove default shadow */
}

/* Adjust Ant Design card internal elements to be transparent/blend */
.info-card :deep(.ant-card-head) {
  background-color: rgba(255, 255, 255, 0.1); /* Slightly visible header background */
  border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* Light border for header */
}
.info-card :deep(.ant-card-head-title) {
  color: #333; /* Darker title for readability against light frosted glass */
}
.info-card :deep(.ant-card-body) {
  background-color: transparent; /* Ensure body itself is transparent */
}


.region-title-wrapper {
  text-align: center;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333; /* Darker color for better contrast on frosted glass */
}

.cities-count-wrapper {
  display: block;
  text-align: center;
  margin-bottom: 24px;
  font-size: 1.5em;
  color: rgba(0, 0, 0, 0.65);
}

.navigation-buttons {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24px;
  gap: 16px;
}

.navigation-buttons .ant-btn {
  flex: 1;
  height: 48px;
  font-size: 1.1em;
}

.map-column {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  height: 100%;
}

.map-container {
  width: 100%;
  height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.3); /* Lighter border for map */
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background-color: rgba(255, 255, 255, 0.1); /* Slight transparent background for map container */
}

.map-element {
  width: 100%;
  height: 100%;
  background-color: #e0e0e0; /* Placeholder background */
}

.map-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.city-list {
  max-height: 400px;
  overflow-y: auto;
  margin-top: 24px;
}

/* Ant Design List styling adjustments for transparency */
.ant-list-item {
  background-color: rgba(255, 255, 255, 0.4); /* Frosted item background */
  border-bottom: 1px solid rgba(255, 255, 255, 0.6); /* Frosted separator */
  color: #333; /* Darker text for list items */
}
.ant-list-item:last-child {
  border-bottom: none;
}
.ant-list-item:hover {
  background-color: rgba(255, 255, 255, 0.6); /* Lighter on hover */
}
.ant-list-item-meta-title {
  margin-bottom: 0;
  color: #333; /* Darker title for list item */
}
.ant-list-item-meta-description {
  color: rgba(0, 0, 0, 0.65); /* Darker description for list item */
}
.ant-list-item-meta {
  align-items: center; /* Vertically align content in list item */
}


/* Fade and Slide Animation */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease-in-out;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .info-column {
    padding-right: 0;
    margin-bottom: 24px;
  }

  .content-row {
    padding: 16px;
    height: auto; /* Allow content to dictate height on mobile */
    flex-direction: column; /* Stack columns vertically on mobile */
  }
  .map-container {
    height: 400px;
  }
}
</style>
