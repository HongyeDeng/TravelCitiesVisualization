<template>
  <div class="text-analytics-container" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <a-row :gutter="[24, 24]" class="analytics-content-row">
      <!-- Left Part: Selection Interface (1/3 width) -->
      <a-col :xs="24" :md="8" class="selection-column">
        <a-card :loading="loadingSelection" class="selection-card">
          <a-typography-title :level="4" class="text-center">Select for Word Cloud</a-typography-title>
          <a-divider />

          <!-- Back Buttons -->
          <div class="back-buttons" v-if="currentLevel !== 'region'">
            <a-button @click="goBack" block size="large">
              Return to {{ previousLevelDisplay }}
            </a-button>
          </div>
          <a-divider v-if="currentLevel !== 'region'" />

          <!-- Region List -->
          <template v-if="currentLevel === 'region'">
            <a-list
              :data-source="regions"
              :loading="loadingRegions"
              item-layout="horizontal"
              class="selection-list"
            >
              <template #renderItem="{ item }">
                <a-list-item @click="selectRegion(item.name)" class="selection-item">
                  <a-list-item-meta :title="item.name" />
                </a-list-item>
              </template>
              <a-empty v-if="!loadingRegions && regions.length === 0" description="No regions found." />
            </a-list>
          </template>

          <!-- Country List -->
          <template v-if="currentLevel === 'country'">
            <a-typography-title :level="5" class="text-center">Countries in {{ selectedRegion }}</a-typography-title>
            <a-list
              :data-source="countries"
              :loading="loadingCountries"
              item-layout="horizontal"
              class="selection-list"
            >
              <template #renderItem="{ item }">
                <a-list-item @click="selectCountry(item.name)" class="selection-item">
                  <a-list-item-meta :title="item.name" />
                </a-list-item>
              </template>
              <a-empty v-if="!loadingCountries && countries.length === 0" description="No countries found in this region." />
            </a-list>
          </template>

          <!-- City List -->
          <template v-if="currentLevel === 'city'">
            <a-typography-title :level="5" class="text-center">Cities in {{ selectedCountry }}</a-typography-title>
            <a-list
              :data-source="cities"
              :loading="loadingCities"
              item-layout="horizontal"
              class="selection-list"
            >
              <template #renderItem="{ item }">
                <a-list-item @click="selectCity(item.name)" class="selection-item">
                  <a-list-item-meta :title="item.name" />
                </a-list-item>
              </template>
              <a-empty v-if="!loadingCities && cities.length === 0" description="No cities found in this country." />
            </a-list>
          </template>
        </a-card>
      </a-col>

      <!-- Right Part: Word Cloud Chart (2/3 width) -->
      <a-col :xs="24" :md="16" class="chart-column">
        <a-card :loading="loadingWordCloud" :title="wordCloudTitle" class="wordcloud-card">
          <v-chart class="chart" :option="wordCloudOption" autoresize /> <!-- Added autoresize -->
          <a-empty v-if="!loadingWordCloud && wordCloudData.length === 0" description="No text data available for word cloud." />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { Card, Row, Col, Typography, Divider, Button, List, Empty } from 'ant-design-vue';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { TitleComponent, TooltipComponent } from 'echarts/components';
import 'echarts-wordcloud'; // Import for word cloud registration

// Define the backend API base URL
const API_BASE_URL = 'http://localhost:5000'; // Ensure this matches your Flask backend's address

// Register necessary ECharts components (if not already done globally in main.ts)
use([
  CanvasRenderer,
  TitleComponent,
  TooltipComponent,
]);

// Hardcoded regions list as requested ("origin regions just a few")
const HARDCODED_REGIONS = [
  { name: "Africa" },
  { name: "Asia" },
  { name: "Europe" },
  { name: "North_America" },
  { name: "Oceania" },
  { name: "South_America" },
  // Add any other regions present in your data
];

// Basic list of common English stop words (can be expanded)
const STOP_WORDS = new Set([
  'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
  'to', 'of', 'in', 'on', 'at', 'by', 'with', 'from', 'as', 'for', 'it', 'its', 'he', 'she',
  'you', 'they', 'we', 'i', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
  'our', 'their', 'this', 'that', 'these', 'those', 'can', 'will', 'would', 'should',
  'could', 'do', 'does', 'did', 'have', 'has', 'had', 'not', 'no', 'yes', 'about', 'above',
  'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
  'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t',
  'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t',
  'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t',
  'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers',
  'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if',
  'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most',
  'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
  'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d',
  'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the',
  'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d',
  'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
  'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what',
  'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why',
  'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve',
  'your', 'yours', 'yourself', 'yourselves'
]);

export default defineComponent({
  name: 'TextAnalytics',
  components: {
    'a-card': Card,
    'a-row': Row,
    'a-col': Col,
    'a-typography-title': Typography.Title,
    'a-divider': Divider,
    'a-button': Button,
    'a-list': List,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
    'a-empty': Empty,
    VChart,
  },
  setup() {
    const currentLevel = ref('region'); // 'region', 'country', 'city'
    const selectedRegion = ref(null);
    const selectedCountry = ref(null);
    const selectedCity = ref(null);

    const regions = ref(HARDCODED_REGIONS); // Initialize with hardcoded regions
    const countries = ref([]);
    const cities = ref([]);
    const wordCloudData = ref([]);

    const loadingSelection = ref(false); // General loading for selection lists
    const loadingRegions = ref(false); // Only used for initial load of regions if not hardcoded
    const loadingCountries = ref(false);
    const loadingCities = ref(false);
    const loadingWordCloud = ref(false);

    // Dynamic background image URL for TextAnalytics
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Adjust this path if different

    // Computed property for back button text
    const previousLevelDisplay = computed(() => {
      if (currentLevel.value === 'country') return 'Regions';
      if (currentLevel.value === 'city') return 'Countries';
      return '';
    });

    // Computed property for word cloud title
    const wordCloudTitle = computed(() => {
      if (selectedCity.value) return `Keywords for ${selectedCity.value}`;
      if (selectedCountry.value) return `Keywords for ${selectedCountry.value}`;
      if (selectedRegion.value) return `Keywords for ${selectedRegion.value}`;
      return 'Global Keywords'; // Default title if nothing selected
    });

    // ECharts Word Cloud Option
    const wordCloudOption = computed(() => {
      if (wordCloudData.value.length === 0 && !loadingWordCloud.value) {
        return {}; // Return empty option if no data and not loading
      }
      return {
        title: {
          text: wordCloudTitle.value,
          left: 'center',
          textStyle: { // Adjust title color for better visibility on frosted glass
            color: '#333'
          }
        },
        tooltip: {
          show: true,
          formatter: '{b}: {c}' // Shows word and its count
        },
        series: [{
          type: 'wordCloud', // This is the key for word cloud
          shape: 'circle', // Can be 'circle', 'cardioid', 'diamond', 'triangle-forward', etc.
          gridSize: 8, // The larger the value, the bigger the space between words.
          sizeRange: [30, 80], // Font size range for words
          rotationRange: [-90, 90], // Rotation range for words
          rotationStep: 45,
          drawOutOfBound: false,
          textStyle: {
            color: function () { // Random color for each word
              return 'rgb(' + [
                Math.round(Math.random() * 160),
                Math.round(Math.random() * 160),
                Math.round(Math.random() * 160)
              ].join(',') + ')';
            },
            emphasis: {
              shadowBlur: 10,
              shadowColor: '#333'
            }
          },
          data: wordCloudData.value,
          animationType: 'scale', // ECharts animation for data update
          animationEasing: 'elasticOut',
          animationDelay: function (idx) {
            return Math.random() * 200;
          }
        }]
      };
    });

    /**
     * --- Data Fetching Functions ---
     */

    // No fetchRegions needed as it's hardcoded for the initial display.
    // const fetchRegions = async () => { ... }

    const fetchCountriesInRegion = async (region) => {
      loadingCountries.value = true;
      loadingSelection.value = true; // Use general loading for selection list
      try {
        // Using your /search_countries endpoint
        const response = await fetch(`${API_BASE_URL}/search_countries?region=${encodeURIComponent(region)}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        // The backend /search_countries returns a list of strings directly
        const data = await response.json();
        countries.value = data.map(name => ({ name })); // Convert string array to [{ name: "Country" }]
      } catch (error) {
        console.error(`Error fetching countries for ${region}:`, error);
        countries.value = [];
      } finally {
        loadingCountries.value = false;
        loadingSelection.value = false;
      }
    };

    const fetchCitiesInCountry = async (country) => {
      loadingCities.value = true;
      loadingSelection.value = true; // Use general loading for selection list
      try {
        // Using your /search_cities endpoint (filtered by country)
        const response = await fetch(`${API_BASE_URL}/search_cities?country=${encodeURIComponent(country)}&limit=1000`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        cities.value = data.map(city => ({ name: city.city })); // Map to { name: "City Name" }
      } catch (error) {
        console.error(`Error fetching cities for ${country}:`, error);
        cities.value = [];
      } finally {
        loadingCities.value = false;
        loadingSelection.value = false;
      }
    };

    const fetchWordCloudText = async (params = {}) => {
      loadingWordCloud.value = true;
      const queryParams = new URLSearchParams(params).toString();
      try {
        // Using your /get_short_description_text endpoint
        const response = await fetch(`${API_BASE_URL}/get_short_description_text?${queryParams}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        processTextForWordCloud(data.text || '');
      } catch (error) {
        console.error('Error fetching word cloud text:', error);
        wordCloudData.value = [];
      } finally {
        loadingWordCloud.value = false;
      }
    };

    /**
     * --- Data Processing for Word Cloud ---
     */
    const processTextForWordCloud = (text) => {
      if (!text) {
        wordCloudData.value = [];
        return;
      }

      // Convert to lowercase and remove punctuation
      const cleanedText = text.toLowerCase().replace(/[.,!?;:"'(){}[\]]/g, '');

      // Tokenize words
      const words = cleanedText.split(/\s+/)
        .filter(word => word.length > 2 && !STOP_WORDS.has(word) && word.trim() !== ''); // Filter short/stop words

      // Count word frequencies
      const wordCounts = {};
      words.forEach(word => {
        wordCounts[word] = (wordCounts[word] || 0) + 1;
      });

      // Convert to array of { name: 'word', value: count } and sort
      const sortedWords = Object.entries(wordCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 100); // Take top 100 words for the cloud

      wordCloudData.value = sortedWords;
    };

    /**
     * --- Navigation and Selection Logic ---
     */
    const selectRegion = (regionName) => {
      selectedRegion.value = regionName;
      selectedCountry.value = null;
      selectedCity.value = null;
      currentLevel.value = 'country';
      fetchCountriesInRegion(regionName); // Fetch countries for this region
      fetchWordCloudText({ region: regionName }); // Update word cloud for this region
    };

    const selectCountry = (countryName) => {
      selectedCountry.value = countryName;
      selectedCity.value = null;
      currentLevel.value = 'city';
      fetchCitiesInCountry(countryName); // Fetch cities for this country
      fetchWordCloudText({ country: countryName }); // Update word cloud for this country
    };

    const selectCity = (cityName) => {
      selectedCity.value = cityName;
      currentLevel.value = 'city'; // Stay at city level, but update word cloud if different city selected
      fetchWordCloudText({ city: cityName }); // Update word cloud for this specific city
    };

    const goBack = () => {
      if (currentLevel.value === 'country') {
        currentLevel.value = 'region';
        selectedRegion.value = null;
        selectedCountry.value = null;
        selectedCity.value = null;
        // Regions are hardcoded, so no need to fetch again
        fetchWordCloudText({}); // Show global word cloud
      } else if (currentLevel.value === 'city') {
        currentLevel.value = 'country';
        selectedCity.value = null;
        // Re-fetch countries for the list based on the still-selected region
        if (selectedRegion.value) {
          fetchCountriesInRegion(selectedRegion.value);
          fetchWordCloudText({ region: selectedRegion.value }); // Word cloud for the region's countries
        } else {
          // Fallback if region was somehow cleared (shouldn't happen with this flow)
          selectedCountry.value = null;
          currentLevel.value = 'region';
          fetchWordCloudText({}); // Fallback to global word cloud
        }
      }
    };

    // Initial data fetch on component mount
    onMounted(() => {
      // Regions are hardcoded, so no initial fetch needed for 'regions' list
      fetchWordCloudText({}); // Show initial global word cloud
    });

    return {
      currentLevel,
      selectedRegion,
      selectedCountry,
      selectedCity,
      regions,
      countries,
      cities,
      wordCloudData,
      loadingSelection,
      loadingRegions, // Keeping for consistency, though not actively used with hardcoded regions
      loadingCountries,
      loadingCities,
      loadingWordCloud,
      previousLevelDisplay,
      wordCloudTitle,
      wordCloudOption,
      selectRegion,
      selectCountry,
      selectCity,
      goBack,
      backgroundImageUrl, // Expose the background image URL
    };
  }
});
</script>

<style scoped>
.text-analytics-container {
  /* This container acts as the full-page element for Text Analytics */
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden; /* Prevent scrollbars on the container itself */
  position: relative;
  
  /* Background image properties - as requested */
  /* background-image is now set via inline style in the template */
  background-size: cover; /* Cover the entire area */
  background-position: center center; /* Center the image */
  background-repeat: no-repeat;
  background-attachment: fixed; /* Fixed relative to the viewport */
  /* Remove background-color here as it will be covered by the image */
}

.analytics-content-row {
  /* This is the main content panel with the frosted glass effect */
  width: 90%;
  height: 90%; /* Occupy 90% height of its parent (text-analytics-container) */
  max-width: 1800px;
  
  /* Frosted glass effect properties - same as JourneyDesigner */
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

.selection-column, .chart-column {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.selection-card, .wordcloud-card {
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
  height: auto;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  padding: 0;
  background-color: transparent; /* Ensure body itself is transparent */
}

.selection-list {
  flex-grow: 1;
  overflow-y: auto;
  margin-top: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3); /* Lighter border for frosted look */
  border-radius: 4px;
  padding: 16px;
  background-color: rgba(255, 255, 255, 0.1); /* Slight transparent background for list */
  height: 400px;
}

/* Ensure individual list items fill width */
.selection-list .ant-list-item {
  width: 100%;
  background-color: rgba(255, 255, 255, 0.4); /* Frosted item background */
  border-bottom: 1px solid rgba(255, 255, 255, 0.6); /* Frosted separator */
  color: #333; /* Darker text for list items */
}
.selection-list .ant-list-item:last-child {
  border-bottom: none;
}
.selection-list .ant-list-item:hover {
  background-color: rgba(255, 255, 255, 0.6); /* Lighter on hover */
}
.ant-list-item-meta-title {
  color: #333; /* Darker title for list item */
}
.ant-list-item-meta-description {
  color: rgba(0, 0, 0, 0.65); /* Darker description for list item */
}

.text-center {
  text-align: center;
}

.back-buttons {
  margin-bottom: 16px;
  padding: 0 16px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 500px;
  padding: 50px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .text-analytics-container {
    padding: 16px;
    height: auto;
    min-height: 100vh;
  }
  .analytics-content-row {
    height: auto;
    padding: 16px;
    flex-direction: column;
  }
  .selection-column, .chart-column {
    height: 400px;
    margin-bottom: 24px;
  }
  .chart-column:last-child, .selection-column:last-child {
    margin-bottom: 0;
  }
  .selection-list {
    padding: 12px;
  }
}
</style>
