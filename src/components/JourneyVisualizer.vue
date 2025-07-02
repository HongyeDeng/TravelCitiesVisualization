<template>
  <div class="journey-visualizer-container" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <a-typography-title :level="2" class="page-title">Journey Data Visualization</a-typography-title>

    <div class="main-content-visualizer-container">
      <!-- Chart Gallery Navigation Buttons -->
      <a-button class="nav-button left-nav" @click="prevChart" :disabled="currentChartIndex === 0">
        <LeftOutlined />
      </a-button>

      <a-button class="nav-button right-nav" @click="nextChart" :disabled="currentChartIndex === charts.length - 1">
        <RightOutlined />
      </a-button>

      <!-- Main Chart Display Area -->
      <a-card :loading="!journeyCities || journeyCities.length === 0" class="chart-card">
        <template v-if="!journeyCities || journeyCities.length === 0">
          <a-empty description="Please design a journey first on the 'Design Your Journey' page." />
        </template>
        <template v-else>
          <!-- Chart Titles -->
          <a-typography-title :level="4" class="chart-title">{{ currentChartTitle }}</a-typography-title>
          <a-divider />

          <!-- Dynamic Chart Component -->
          <div v-if="currentChartIndex === 0" class="chart-wrapper">
            <v-chart class="chart" :option="dotPlotOption" autoresize />
          </div>
          <div v-else-if="currentChartIndex === 1" class="chart-wrapper">
            <v-chart class="chart" :option="themeRiverOption" autoresize />
          </div>
          <div v-else-if="currentChartIndex === 2" class="chart-wrapper radar-chart-layout">
            <!-- Radar Chart: Left (List) and Right (Chart) -->
            <div class="radar-city-list-wrapper">
              <a-typography-title :level="5">Select Cities for Average</a-typography-title>
              <a-list
                size="small"
                :data-source="journeyCities"
                class="radar-city-list"
              >
                <template #renderItem="{ item }">
                  <a-list-item @click="toggleRadarCitySelection(item.id)" :class="{'selected-radar-city': isRadarCitySelected(item.id)}">
                    {{ item.city }}, {{ item.country }}
                  </a-list-item>
                </template>
                <a-empty v-if="journeyCities.length === 0" description="No cities in journey." />
              </a-list>
            </div>
            <div class="radar-chart-area">
              <v-chart class="chart" :option="radarChartOption" autoresize />
            </div>
          </div>
        </template>
      </a-card>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { Card, Button, Typography, Empty, Divider, List, message } from 'ant-design-vue';
import { LeftOutlined, RightOutlined } from '@ant-design/icons-vue';

// ECharts imports and registration for this component only
// Import only the modules required for THIS page
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent, // For Cartesian charts (Dot Plot)
  XAxisComponent,
  YAxisComponent,
  VisualMapComponent, // For ThemeRiver, potentially Dot Plot color mapping
  RadarComponent,
  SingleAxisComponent  // For Radar Chart
} from 'echarts/components';
import {
  ScatterChart, // For Dot Plot
  ThemeRiverChart, // For ThemeRiver
  RadarChart // For Radar Chart
} from 'echarts/charts';

// Register the necessary ECharts modules for this component
use([
  CanvasRenderer,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
  RadarComponent,
  ScatterChart,
  ThemeRiverChart,
  RadarChart,
  SingleAxisComponent,
]);

import { useJourneyStore } from '../stores/journey';

export default defineComponent({
  name: 'JourneyVisualizer',
  components: {
    'a-card': Card,
    'a-button': Button,
    'a-typography-title': Typography.Title,
    'a-empty': Empty,
    'a-divider': Divider,
    'a-list': List,
    'a-list-item': List.Item,
    LeftOutlined,
    RightOutlined,
    VChart,
  },
  setup() {
    const journeyStore = useJourneyStore();
    const journeyCities = computed(() => journeyStore.getJourneyCities);

    const currentChartIndex = ref(0); // 0: Dot Plot, 1: ThemeRiver, 2: Radar Chart

    // Dynamic background image URL for JourneyVisualizer
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Adjust this path if different

    // List of rating properties
    const ratingProperties = [
      'culture', 'adventure', 'nature', 'beaches', 'nightlife',
      'cuisine', 'wellness', 'urban', 'seclusion'
    ];

    // Chart titles for gallery navigation
    const charts = [
      { title: 'Budget & Property Ratings Dot Plot' },
      { title: 'Journey Theme River Flow' },
      { title: 'Average Property Ratings Radar Chart' },
    ];
    const currentChartTitle = computed(() => charts[currentChartIndex.value].title);

    // --- Radar Chart Specific State ---
    // Initially, all cities in the journey are selected for the radar chart average
    const selectedRadarCityIds = ref(new Set());

    // Watch journeyCities to update selectedRadarCityIds when the journey changes
    watch(journeyCities, (newCities) => {
        // Reset selected cities to all new cities whenever journeyCities changes
        selectedRadarCityIds.value = new Set(newCities.map(city => city.id));
    }, { immediate: true, deep: true }); // Immediate to set initial state, deep to react to inner changes

    const isRadarCitySelected = (cityId) => selectedRadarCityIds.value.has(cityId);

    const toggleRadarCitySelection = (cityId) => {
      if (selectedRadarCityIds.value.has(cityId)) {
        if (selectedRadarCityIds.value.size > 1) { // Prevent deselecting last city
          selectedRadarCityIds.value.delete(cityId);
        } else {
          message.warn('At least one city must be selected for the Radar Chart.');
        }
      } else {
        selectedRadarCityIds.value.add(cityId);
      }
      // Trigger reactivity for computed properties that depend on selectedRadarCityIds
      selectedRadarCityIds.value = new Set(selectedRadarCityIds.value); // Create new Set to trigger update
    };

    /**
     * --- Chart Options Computed Properties ---
     */

    // 1. Dot Plot Option
    const dotPlotOption = computed(() => {
      if (!journeyCities.value || journeyCities.value.length === 0) return {};

      const xAxisData = journeyCities.value.map(city => city.city);
      const series = [];

      // Budget Level Series
      const budgetData = journeyCities.value.map((city, index) => {
        let size = 15; // Default size
        let color = '#ccc'; // Default color
        let opacity = 0.6;

        switch (String(city.budget_level).toLowerCase()) {
          case 'luxury':
            color = '#FFD700'; // Gold
            size = 20; // Bigger dot for luxury
            opacity = 1;
            break;
          case 'mid-range':
            color = '#87CEEB'; // SkyBlue
            size = 15;
            opacity = 0.8;
            break;
          case 'budget':
            color = '#DAA520'; // Goldenrod
            size = 10; // Smaller dot for budget
            opacity = 0.4;
            break;
        }
        return { value: [index, 0], itemStyle: { color: color, opacity: opacity }, symbolSize: size };
      });
      series.push({
        name: 'Budget Level',
        type: 'scatter',
        data: budgetData,
        yAxisIndex: 0, // Maps to the first category axis (Budget Level)
        tooltip: {
          formatter: function (param) {
            //return `${xAxisData[param.data[0]]}: Budget Level - ${journeyCities.value[param.data[0]].budget_level}`;
            return '';
          },
        },
        zlevel: 2 // Bring budget dots to front
      });

      // Rating Properties Series
      ratingProperties.forEach((prop, propIndex) => {
        const ratingSeriesData = journeyCities.value.map((city, cityIndex) => {
          const rating = city[prop] || 0;
          let size = 8 + (rating * 2); // Scale size by rating
          let color;
          let opacity = 0.7 + (rating * 0.05); // Slightly increase opacity with rating

          // Different color themes for different properties
          const colorTheme = {
            'culture': ['#B0C4DE', '#4682B4'], // LightSteelBlue to SteelBlue
            'adventure': ['#90EE90', '#32CD32'], // LightGreen to LimeGreen
            'nature': ['#FFB6C1', '#FF69B4'], // LightPink to HotPink
            'beaches': ['#ADD8E6', '#87CEEB'], // LightBlue to SkyBlue
            'nightlife': ['#DDA0DD', '#9932CC'], // Plum to DarkOrchid
            'cuisine': ['#FFE4B5', '#FF8C00'], // Moccasin to DarkOrange
            'wellness': ['#E0BBE4', '#957DAD'], // Plum to DarkSlateBlue
            'urban': ['#F0F8FF', '#4169E1'], // AliceBlue to RoyalBlue
            'seclusion': ['#F5DEB3', '#D2B48C']  // Wheat to Tan
          };
          
          const [lowColor, highColor] = colorTheme[prop] || ['#ccc', '#666']; // Default if not found

          // Simple linear interpolation for color
          const interpolateColor = (c1, c2, factor) => {
              const hexToRgb = hex => [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
              const rgbToHex = rgb => '#' + rgb.map(x => Math.round(x).toString(16).padStart(2, '0')).join('');

              const rgb1 = hexToRgb(c1);
              const rgb2 = hexToRgb(c2);

              const r = rgb1[0] + factor * (rgb2[0] - rgb1[0]);
              const g = rgb1[1] + factor * (rgb2[1] - rgb1[1]);
              const b = rgb1[2] + factor * (rgb2[2] - rgb1[2]);

              return rgbToHex([r, g, b]);
          };

          color = interpolateColor(lowColor, highColor, rating / 5.0);

          return { value: [cityIndex, propIndex + 1], itemStyle: { color: color, opacity: opacity }, symbolSize: size }; // +1 because budget is at 0
        });

        series.push({
          name: prop.charAt(0).toUpperCase() + prop.slice(1),
          type: 'scatter',
          data: ratingSeriesData,
          yAxisIndex: 0,
        //   tooltip: {
        //     formatter: function (param) {
        //       return `${xAxisData[param.data[0]]}: ${prop.charAt(0).toUpperCase() + prop.slice(1)} - ${journeyCities.value[param.data[0]][prop]}`;
        //     }
        //   },
          zlevel: 1 // Ratings slightly behind budget
        });
      });

      return {
        tooltip: {
          trigger: 'item',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['Budget Level', ...ratingProperties.map(prop => prop.charAt(0).toUpperCase() + prop.slice(1))],
          bottom: 0,
          type: 'scroll',
          textStyle: { // Adjust legend text color
            color: '#333'
          }
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          axisTick: { alignWithLabel: true },
          name: 'City',
          axisLabel: {
            color: '#333' // Axis label color
          },
          axisLine: {
            lineStyle: {
              color: '#666' // Axis line color
            }
          }
        },
        yAxis: {
          type: 'category',
          data: ['Budget Level', ...ratingProperties.map(prop => prop.charAt(0).toUpperCase() + prop.slice(1))],
          axisLabel: {
            formatter: function (value) {
              return value.replace('Rating', '').trim();
            },
            color: '#333' // Axis label color
          },
          axisLine: {
            lineStyle: {
              color: '#666' // Axis line color
            }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          top: '10%',
          bottom: '10%',
          containLabel: true
        },
        series: series
      };
    });

    // 2. ThemeRiver Option
    const themeRiverOption = computed(() => {
        if (!journeyCities.value || journeyCities.value.length === 0) return {};

        const data = [];
        // Structure for ThemeRiver: [time, value, name]
        // time here will be the index of the city in the journey
        // name will be the property (e.g., culture, adventure)
        // value will be the rating

        journeyCities.value.forEach((city, cityIndex) => {
            ratingProperties.forEach(prop => {
                const rating = city[prop] || 0;
                const poweredRating = Math.pow(rating, 2);
                // ThemeRiver expects value to be positive. If rating is 0, it won't show.
                // We'll scale 0-5 to 1-6 for visibility, or handle 0 as a small base.
                data.push([cityIndex, poweredRating + 1, prop.charAt(0).toUpperCase() + prop.slice(1)]);
            });
        });

        console.log('Get ThemeRiver Data');

        const distinctThemes = ratingProperties.map(prop => prop.charAt(0).toUpperCase() + prop.slice(1));
        const xAxisLabels = journeyCities.value.map(city => city.city);

        return {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'line',
                    lineStyle: {
                        color: 'rgba(0,0,0,0.2)',
                        width: 1,
                        type: 'solid'
                    }
                },
                formatter: function (params) {
                    let res = `<b>${xAxisLabels[params[0].value[0]]}</b><br/>`;
                    params.forEach(item => {
                        // item.name is the series name (property), item.value[1] is the value (rating + 1)
                        res += `${item.marker} ${item.name}: ${item.value[1] - 1}<br/>`; // Subtract 1 to show actual rating
                    });
                    return res;
                }
            },
            legend: {
                data: distinctThemes,
                bottom: 0,
                type: 'scroll',
                textStyle: { // Adjust legend text color
                  color: '#333'
                }
            },
            singleAxis: {
                top: 50,
                bottom: 50,
                type: 'category',
                axisTick: {},
                axisLabel: {
                    interval: 0, // Show all labels
                    rotate: 45, // Rotate labels for better readability
                    formatter: function(value, index) {
                        return xAxisLabels[index];
                    },
                    color: '#333' // Axis label color
                },
                axisLine: {
                  lineStyle: {
                    color: '#666' // Axis line color
                  }
                },
                splitLine: {
                    show: true,
                    lineStyle: {
                        type: 'dashed',
                        opacity: 0.2
                    }
                },
                data: xAxisLabels // City names as x-axis categories
            },
            series: [{
                type: 'themeRiver',
                emphasis: {
                    itemStyle: {
                        shadowBlur: 20,
                        shadowColor: 'rgba(0, 0, 0, 0.4)'
                    }
                },
                data: data,
                smooth: true,
                selectedMode: 'single', // Allows single selection
                itemStyle: {
                    // Random color for each theme, or specific colors can be mapped
                    color: function(params) {
                        const colors = ['#5470C6', '#91CC75', '#EE6666', '#73C0DE', '#3BA272', '#FC8452', '#9A60B4', '#EA7CCC', '#F7B851'];
                        return colors[distinctThemes.indexOf(params.name) % colors.length];
                    }
                }
            }]
        };
    });

    // 3. Radar Chart Option
    const radarChartOption = computed(() => {
        const citiesToAverage = journeyCities.value.filter(city =>
            selectedRadarCityIds.value.has(city.id)
        );

        if (citiesToAverage.length === 0) {
            return {};
        }

        const averageRatings = {};
        ratingProperties.forEach(prop => {
            const sum = citiesToAverage.reduce((acc, city) => acc + (Number(city[prop]) || 0), 0);
            averageRatings[prop] = sum / citiesToAverage.length;
        });

        const indicators = ratingProperties.map(prop => ({
            name: prop.charAt(0).toUpperCase() + prop.slice(1),
            max: 5,
            min: 0
        }));

        return {
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    const seriesName = params.name;
                    let res = `${seriesName}:<br/>`;
                    params.data.value.forEach((val, index) => {
                        res += `${indicators[index].name}: ${val.toFixed(1)}<br/>`;
                    });
                    return res;
                }
            },
            radar: {
                indicator: indicators,
                radius: '70%',
                center: ['50%', '55%'],
                name: {
                    color: '#333'
                },
                // --- ENHANCED GRID STYLES ---
                splitArea: { // Background areas between radar lines
                    show: true,
                    areaStyle: {
                        color: [
                            'rgba(182, 182, 182, 0.2)',  // Darker shade 1
                            'rgba(182, 182, 182, 0.3)',  // Darker shade 2
                            'rgba(182, 182, 182, 0.4)',  // Darker shade 3
                            'rgba(182, 182, 182, 0.5)',  // Darker shade 4
                            'rgba(182, 182, 182, 0.6)'   // Darker shade 5
                        ].reverse() // Reverse to make center darker
                    }
                },
                axisLine: { // Lines connecting center to indicators (spokes)
                    lineStyle: {
                        color: 'rgba(0, 0, 0, 0.5)', // Darker axis lines
                        width: 2 // Thicker axis lines
                    }
                },
                splitLine: { // Concentric grid lines
                    lineStyle: {
                        color: 'rgba(0, 0, 0, 0.3)', // Darker grid lines
                        width: 1 // Standard width
                    }
                }
                // --- END ENHANCED GRID STYLES ---
            },
            series: [
                {
                    name: 'Average Ratings',
                    type: 'radar',
                    data: [{
                        value: ratingProperties.map(prop => averageRatings[prop]),
                        name: 'Average Ratings',
                        itemStyle: {
                            color: '#1890ff'
                        },
                        areaStyle: {
                            color: 'rgba(24, 144, 255, 0.3)'
                        }
                    }]
                }
            ]
        };
    });

    /**
     * --- Chart Gallery Navigation ---
     */
    const nextChart = () => {
      if (currentChartIndex.value < charts.length - 1) {
        currentChartIndex.value++;
      }
    };

    const prevChart = () => {
      if (currentChartIndex.value > 0) {
        currentChartIndex.value--;
      }
    };

    return {
      journeyCities,
      currentChartIndex,
      charts,
      currentChartTitle,
      dotPlotOption,
      themeRiverOption,
      radarChartOption,
      nextChart,
      prevChart,
      selectedRadarCityIds,
      isRadarCitySelected,
      toggleRadarCitySelection,
      backgroundImageUrl, // Expose the background image URL
    };
  }
});
</script>

<style scoped>
.journey-visualizer-container {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden; /* Prevent scrollbars on the container itself */
  position: relative;
  
  /* Background image properties - as requested */
  background-size: cover; /* Cover the entire area */
  background-position: center center; /* Center the image */
  background-repeat: no-repeat;
  background-attachment: fixed; /* Fixed relative to the viewport */
  /* Remove background-color here as it will be covered by the image */
}

.page-title {
  text-align: center;
  margin-bottom: 24px;
  color: #fff; /* Changed to white for better contrast on background image */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); /* Stronger shadow for readability */
}

.main-content-visualizer-container {
  position: relative;
  width: 90%;
  height: 90vh;
  max-width: 1800px;
  
  /* Frosted glass effect properties - same as JourneyDesigner */
  background-color: rgba(255, 255, 255, 0.2); /* Semi-transparent white */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  -webkit-backdrop-filter: blur(10px); /* For Safari support */
  border-radius: 12px; /* Rounded corners */
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); /* Subtle shadow */
  border: 1px solid rgba(255, 255, 255, 0.18); /* Light border */
  
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden;
}

.chart-card {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  box-shadow: none; /* Remove default Ant Card shadow */
  display: flex;
  flex-direction: column;
  background-color: transparent; /* Make card transparent to let frosted glass show through */
}

/* Ensure card body takes remaining space */
.ant-card :deep(.ant-card-body) {
  flex-grow: 1;
  height: auto;
  display: flex;
  flex-direction: column;
  padding: 24px;
  background-color: transparent; /* Ensure body itself is transparent */
}

/* Adjust Ant Design card head padding/background for frosted glass */
.ant-card :deep(.ant-card-head) {
  background-color: rgba(255, 255, 255, 0.1); /* Slightly visible header background */
  border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* Light border for header */
}
.ant-card :deep(.ant-card-head-title) {
  color: #333; /* Darker title for readability against light frosted glass */
}


.chart-title {
  text-align: center;
  margin-bottom: 16px !important;
  color: #333; /* Darker title for readability against frosted glass */
}

.chart-wrapper {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.left-nav {
  left: -25px;
}

.right-nav {
  right: -25px;
}

.nav-button:hover:not([disabled]) {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.nav-button[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Radar Chart Specific Layout */
.radar-chart-layout {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  justify-content: center;
  align-items: flex-start;
}

.radar-city-list-wrapper {
  flex: 1;
  padding-right: 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
}

.radar-city-list {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.3); /* Lighter border for frosted look */
  border-radius: 4px;
  padding: 8px 0;
  background-color: rgba(255, 255, 255, 0.1); /* Slight transparent background for list */
  color: #333; /* Darker text for readability */
}

.radar-city-list .ant-list-item {
  cursor: pointer;
  padding: 8px 16px;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.6); /* Frosted separation */
}

.radar-city-list .ant-list-item:last-child {
  border-bottom: none;
}

.radar-city-list .ant-list-item:hover {
  background-color: rgba(255, 255, 255, 0.4); /* Lighter on hover */
}

.selected-radar-city {
  background-color: rgba(173, 216, 230, 0.7); /* Light blue with transparency */
  font-weight: bold;
}

.radar-chart-area {
  flex: 2;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255,255,255,0.05); /* Slight transparent background for the chart area */
  border-radius: 8px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .main-content-visualizer-container {
    width: 100%;
    height: auto;
    padding: 16px;
  }
  .nav-button {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  .left-nav {
    left: 5px;
  }
  .right-nav {
    right: 5px;
  }

  .chart-card :deep(.ant-card-body) {
    padding: 16px;
  }
  .chart-title {
    font-size: 1.5em;
  }

  .radar-chart-layout {
    flex-direction: column;
  }
  .radar-city-list-wrapper {
    padding-right: 0;
    margin-bottom: 24px;
    height: 250px;
  }
  .radar-chart-area {
    height: 300px;
  }
}
</style>
