<template>
  <div
    id="app"
    :style="{
      backgroundImage: 'url(' + backgroundImageUrl + ')',
      backgroundSize: 'cover',
      backgroundPosition: 'center center',
      backgroundAttachment: 'fixed',
      backgroundRepeat: 'no-repeat'
    }"
  >
    <!-- Left Scroll Hotzone -->
    <div class="scroll-hotzone left-hotzone" @wheel.prevent="handleMouseWheel"></div>

    <!-- Right Scroll Hotzone -->
    <div class="scroll-hotzone right-hotzone" @wheel.prevent="handleMouseWheel"></div>

    <!-- Main Content Sections Wrapper - No longer directly captures global scroll events -->
    <div class="app-sections-wrapper">
      <div id="homepage-section" class="app-section">
        <!-- Add listener for 'scroll-to-regions' event from HomePage -->
        <HomePage @scroll-to-regions="scrollToSection(1)" />
      </div>

      <div id="region-explorer-section" class="app-section">
        <RegionExplorer />
      </div>

      <div id="analytics-dashboard-section" class="app-section">
        <AnalyticsDashboard />
      </div>

      <div id="city-detail-section" class="app-section">
        <CityDetailExplorer />
      </div>

      <div id="text-analytics-section" class="app-section">
        <TextAnalytics />
      </div>

      <div id="journey-designer-section" class="app-section">
        <JourneyDesigner />
      </div>

      <div id="journey-visualizer-section" class="app-section">
        <JourneyVisualizer />
      </div>

      <div id="City-Image-Gallery-section" class="app-section">
        <CityImageGallery />
      </div>

      <div id="App-Footer-section" class="footer-section">
        <AppFooter />
      </div>

    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount, computed } from 'vue';
import HomePage from './components/Homepage.vue';
import RegionExplorer from './components/RegionExplorer.vue';
import AnalyticsDashboard from './components/AnalyticsDashboard.vue'; 
import TextAnalytics from './components/TextAnalytics.vue';
import CityDetailExplorer from './components/CityDetailExplorer.vue';
import JourneyDesigner from './components/JourneyDesigner.vue';
import JourneyVisualizer from './components/JourneyVisualizer.vue';
import CityImageGallery from './components/CityImageGallery.vue';
import AppFooter from './components/AppFooter.vue';

export default defineComponent({
  name: 'App',
  components: {
    HomePage,
    RegionExplorer,
    AnalyticsDashboard,
    TextAnalytics,
    CityDetailExplorer,
    JourneyDesigner,
    JourneyVisualizer,
    CityImageGallery,
    AppFooter,
  },
  setup() {
    const backgroundImageUrl = ref('/images/your-journey-background.jpg'); // SET YOUR GLOBAL BACKGROUND IMAGE HERE

    const sections = [
      'homepage-section',
      'region-explorer-section',
      'analytics-dashboard-section',
      'city-detail-section',
      'text-analytics-section',
      'journey-designer-section',
      'journey-visualizer-section',
      'City-Image-Gallery-section',
      'App-Footer-section'
    ];
    const currentSectionIndex = ref(0);

    // Scroll snapping state variables
    const scrollDeltaY = ref(0);
    const scrollThreshold = 100; // Pixels to scroll before snapping to next section
    const isSnapping = ref(false); // Flag to prevent multiple snaps during animation
    const snapDuration = 800; // Duration of the scroll animation in milliseconds

    let observers = []; // To store IntersectionObserver instances

    /**
     * Scrolls to the section at the given index.
     * @param {number} index - The index of the section to scroll to.
     */
    const scrollToSection = (index) => {
      if (isSnapping.value || index < 0 || index >= sections.length) {
        return;
      }

      isSnapping.value = true;
      const sectionId = sections[index];
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
        currentSectionIndex.value = index;

        setTimeout(() => {
          isSnapping.value = false;
          scrollDeltaY.value = 0;
        }, snapDuration);
      } else {
        isSnapping.value = false;
      }
    };

    /**
     * Navigates to the next page/section.
     */
    const nextPage = () => {
      if (currentSectionIndex.value < sections.length - 1) {
        scrollToSection(currentSectionIndex.value + 1);
      }
    };

    /**
     * Navigates to the previous page/section.
     */
    const prevPage = () => {
      if (currentSectionIndex.value > 0) {
        scrollToSection(currentSectionIndex.value - 1);
      }
    };

    /**
     * Handles mouse wheel events for custom scroll snapping.
     * This function is now only triggered by the "hotzone" divs.
     * @param {WheelEvent} event - The mouse wheel event.
     */
    const handleMouseWheel = (event) => {
      event.preventDefault(); // Prevents default scroll behavior for the hotzone area

      if (isSnapping.value) {
        return;
      }

      scrollDeltaY.value += event.deltaY;

      if (Math.abs(scrollDeltaY.value) >= scrollThreshold) {
        if (scrollDeltaY.value > 0) { // Scrolling down
          nextPage();
        } else { // Scrolling up
          prevPage();
        }
        scrollDeltaY.value = 0;
      }
    };

    onMounted(() => {
      // IntersectionObserver setup for robust index tracking
      const appSectionsWrapper = document.querySelector('.app-sections-wrapper');
      if (appSectionsWrapper) {
        sections.forEach((sectionId, index) => {
          const section = document.getElementById(sectionId);
          if (section) {
            const observer = new IntersectionObserver((entries) => {
              entries.forEach(entry => {
                if (entry.isIntersecting && entry.intersectionRatio >= 0.7 && !isSnapping.value) {
                  currentSectionIndex.value = index;
                }
              });
            }, {
              root: appSectionsWrapper, // Observe within the scrollable wrapper
              threshold: 0.7
            });
            observer.observe(section);
            observers.push(observer);
          }
        });
      }
    });

    onBeforeUnmount(() => {
      // Disconnect all observers
      observers.forEach(observer => observer.disconnect());
    });

    return {
      backgroundImageUrl,
      sections,
      currentSectionIndex,
      handleMouseWheel, // Expose the wheel handler to the template for hotzones
      scrollToSection, // Expose scrollToSection for HomePage's explore button
    };
  }
});
</script>

<style>
/* Global styles for your application */
html, body {
  margin: 0;
  height: 100%;
  overflow: hidden; /* Prevent native scrolling on html/body */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-smoothing: grayscale;
  overflow-x: hidden;
  scroll-behavior: auto !important; /* Explicitly disable any default smooth scrolling */
}

#app {
  width: 100vw;
  height: 100vh; /* App takes full viewport height */
  display: flex;
  position: relative; /* For positioning hotzones relative to #app */
  overflow: hidden; /* Prevent #app from scrolling itself */

  /* IMPORTANT: Background properties are now handled by inline style in the template */
}

/* --- NEW CSS RULES FOR SCROLL HOTZONES --- */
.scroll-hotzone {
  position: fixed; /* Fixed relative to the viewport */
  top: 0;
  height: 100vh;
  width: 5vw; /* Take 10% of viewport width on each side */
  z-index: 100; /* Ensure it's above other content */
  /* background-color: rgba(0, 255, 0, 0.1); /* Uncomment for debugging visibility */
  pointer-events: auto; /* Ensure it can capture mouse events */
}

.left-hotzone {
  left: 0;
}

.right-hotzone {
  right: 0;
}
/* --- END NEW CSS RULES FOR SCROLL HOTZONES --- */


.app-sections-wrapper {
  flex-grow: 1; /* Allows this wrapper to take up remaining horizontal space */
  display: flex;
  flex-direction: column; /* Stack sections vertically */
  width: 100%; /* Take full width of its parent (#app) */
  height: 100vh; /* Important: Make this wrapper take full viewport height */
  overflow-y: scroll; /* Enable vertical scrolling ONLY for this wrapper (for internal content) */
}

.app-section {
  width: 100%;
  min-height: 100vh; /* Each section takes up at least a full viewport height */
  display: flex; /* Use flexbox to center content vertically within the section */
  justify-content: center; /* Center horizontally */
  align-items: center; /* Center vertically */
  box-sizing: border-box; /* Include padding in height calculation */
  padding: 0px; /* Default padding for sections */
  flex-shrink: 0; /* Prevent sections from shrinking below 100vh */
}

.footer-section {
    width: 100%;
  min-height: 100vh; /* Each section takes up at least a full viewport height */
  display: flex; /* Use flexbox to center content vertically within the section */
  justify-content: center; /* Center horizontally */
  align-items: center; /* Center vertically */
  box-sizing: border-box; /* Include padding in height calculation */
  padding: 0px; /* Default padding for sections */
  flex-shrink: 0; /* Prevent sections from shrinking below 100vh */
}

/* Specific styling for HomePage within its section to enable full background */
#homepage-section {
  padding: 0; /* HomePage content will manage its own padding/centering */
}

/* Adjustments for fixed background to work with inner frosted glass elements */
/* These styles allow the global fixed background to show through sections */
#homepage-section,
#region-explorer-section,
#analytics-dashboard-section,
#city-detail-section,
#text-analytics-section,
#journey-designer-section,
#journey-visualizer-section {
  /* Ensure these sections are transparent so the #app background shows through.
     The frosted glass effect will be applied to inner content containers. */
  background-color: transparent;
}

/* Responsive adjustments for mobile */
@media (max-width: 768px) {
  .scroll-hotzone {
    width: 10vw; /* Increase hotzone width on smaller screens if needed */
  }
}
</style>
