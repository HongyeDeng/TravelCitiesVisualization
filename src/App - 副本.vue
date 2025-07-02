<template>
  <div id="app">
    <!-- HomePage as the first section -->
    <!-- Listens for the custom event 'scroll-to-regions' emitted by HomePage -->
    <HomePage @scroll-to-regions="scrollToRegionExplorer" />

        <div id="region-explorer-section">
      <RegionExplorer />
      <!-- The "View Analytics" button and its container have been removed from here. -->
    </div>

    <!-- Analytics Dashboard as the third section -->
    <!-- It also needs a unique ID for scrolling -->
    <div id="analytics-dashboard-section">
      <AnalyticsDashboard />
    </div>

    <div id="city-detail-section">
      <CityDetailExplorer />
    </div>

    <div id="text-analytics-section">
      <TextAnalytics />
    </div>

    <div id="journey-designer-section">
      <JourneyDesigner />
    </div>

    <div id="journey-visualizer-section">
      <JourneyVisualizer />
    </div>
  </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import HomePage from './components/Homepage.vue';
import RegionExplorer from './components/RegionExplorer.vue';
import AnalyticsDashboard from './components/AnalyticsDashboard.vue'; 
import TextAnalytics from './components/TextAnalytics.vue';
import CityDetailExplorer from './components/CityDetailExplorer.vue';
import JourneyDesigner from './components/JourneyDesigner.vue';
import JourneyVisualizer from './components/JourneyVisualizer.vue';
// The 'Button' component import is removed as it's no longer used directly in App.vue

export default defineComponent({
  name: 'App',
  components: {
    HomePage,
    RegionExplorer,
    AnalyticsDashboard, // Register the AnalyticsDashboard component
    TextAnalytics, // Register the TextAnalytics component
    CityDetailExplorer,
    JourneyDesigner,
    JourneyVisualizer,
    // 'a-button' is no longer registered here as the button is removed
  },
  setup() {
    /**
     * Scrolls the page down to the Region Explorer section.
     * This function is triggered by the 'scroll-to-regions' event from HomePage.
     */
    const scrollToRegionExplorer = () => {
      const regionExplorerSection = document.getElementById('region-explorer-section');
      if (regionExplorerSection) {
        regionExplorerSection.scrollIntoView({ behavior: 'smooth' });
      }
    };

    // The scrollToAnalyticsDashboard function has been removed.

    // Ensure smooth scroll behavior is applied to the entire page.
    // This is set both in global CSS and explicitly here via JS for robustness.
    onMounted(() => {
      document.documentElement.style.scrollBehavior = 'smooth';
      document.body.style.scrollBehavior = 'smooth';
    });

    return {
      scrollToRegionExplorer,
      // scrollToAnalyticsDashboard is no longer returned as it's removed.
    };
  }
});
</script>

<style>
/* Global styles for your application */
body {
  margin: 0; /* Resets default browser margin on the body */
  /* Ant Design's recommended font stack for consistency */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden; /* Prevent horizontal scroll bar from appearing */
  scroll-behavior: smooth; /* Enables smooth scrolling for all scroll actions on the page */
}

#app {
  /* This container holds the full-page scrollable content. */
  /* min-height ensures it expands to at least the viewport height to allow scrolling */
  width: 100vw;
  min-height: 100vh;
}

/* The style for .navigation-to-dashboard has been removed. */


/* Ensure each major section takes up at least full viewport height */
/* This is important for smooth scrolling between distinct "pages" */
#region-explorer-section,
#analytics-dashboard-section {
  min-height: 100vh; /* Make each section at least a full viewport height */
  /* Ensures the section background matches the semi-transparent overlay you want */
  background-color: rgba(255, 255, 255, 0.7); /* Match RegionExplorer's container background */
  box-sizing: border-box; /* Include padding in height calculation */
  padding: px; /* Add padding to prevent content from touching edges */
}
</style>
