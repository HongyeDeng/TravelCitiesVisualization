<template>
  <div class="city-image-gallery-container"  :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
    <a-typography-title :level="2" class="page-title">City Image Gallery</a-typography-title>

    <div class="gallery-main-panel">
      <template v-if="loadingImages">
        <div class="loading-overlay">
          <a-spin size="large" :tip="`Loading images for ${currentCityName}...`" />
        </div>
      </template>
      <template v-else-if="!currentCity">
        <a-empty description="Please design a journey first or select a city." />
      </template>
      <template v-else-if="cityImages.length === 0">
        <a-empty :description="`No images found for ${currentCityName}.`" />
      </template>
      <template v-else>
        <!-- Image Gallery Display -->
        <div class="image-gallery-display">
          <div class="image-gallery-track" ref="imageGalleryTrack">
            <img
              v-for="(image, index) in cityImages"
              :key="index"
              :src="image"
              alt="City image"
              class="gallery-image"
              @error="handleImageError"
            />
          </div>
        </div>

        <!-- Image Navigation Buttons (over the gallery) -->
        <a-button
          class="nav-button image-nav left-nav"
          @click="prevImage"
          :disabled="currentImageIndex === 0 || loadingImages"
        >
          <LeftOutlined />
        </a-button>
        <a-button
          class="nav-button image-nav right-nav"
          @click="nextImage"
          :disabled="currentImageIndex === cityImages.length - 1 || loadingImages"
        >
          <RightOutlined />
        </a-button>
      </template>

      <!-- City Information and Navigation (at the bottom) -->
      <div class="city-navigation-section">
        <div class="city-info-display">
          <a-typography-title :level="4" class="city-name-text">
            {{ currentCity ? currentCity.city + ', ' + currentCity.country : 'No City Selected' }}
          </a-typography-title>
        </div>
        <div class="city-nav-buttons">
          <a-button
            type="primary"
            size="large"
            @click="prevCity"
            :disabled="currentCityIndex === 0 || loadingImages || !journeyCities || journeyCities.length === 0"
          >
            Previous City
          </a-button>
          <a-button
            type="primary"
            size="large"
            @click="nextCity"
            :disabled="currentCityIndex === journeyCities.length - 1 || loadingImages || !journeyCities || journeyCities.length === 0"
          >
            Next City
          </a-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed, watch, nextTick } from 'vue';
import { Button, Typography, Empty, Spin, message } from 'ant-design-vue'; // Removed Card import
import { LeftOutlined, RightOutlined } from '@ant-design/icons-vue';
import { useJourneyStore } from '../stores/journey';

export default defineComponent({
  name: 'CityImageGallery',
  components: {
    // 'a-card': Card, // Removed unused component registration
    'a-button': Button,
    'a-typography-title': Typography.Title,
    'a-empty': Empty,
    'a-spin': Spin,
    LeftOutlined,
    RightOutlined,
  },
  setup() {
    const backgroundImageUrl = ref('/images/Cover.jpg'); // Adjust this path to your desired image
    const journeyStore = useJourneyStore();
    const journeyCities = computed(() => journeyStore.getJourneyCities);

    // !! IMPORTANT: REPLACE WITH YOUR ACTUAL UNSPLASH ACCESS KEY !!
    const UNSPLASH_ACCESS_KEY = 'hknoxsoMx96azNCfXY2gjpk8fHBnbGXKdOtT9Kc5nwI'; // Replace this line

    const currentCityIndex = ref(0); // Index for navigating between cities in the journey
    const currentImageIndex = ref(0); // Index for navigating images within the current city
    const cityImages = ref([]); // Stores image URLs for the current city
    const loadingImages = ref(false); // Loading state for image fetching

    const imageGalleryTrack = ref(null); // Ref to the image gallery div for scrolling

    const currentCity = computed(() => {
      if (!journeyCities.value || journeyCities.value.length === 0) {
        return null;
      }
      return journeyCities.value[currentCityIndex.value];
    });

    const currentCityName = computed(() => {
      return currentCity.value ? `${currentCity.value.city}, ${currentCity.value.country}` : 'Loading City...';
    });

    /**
     * Fetches images for a given city from Unsplash API.
     * @param {string} cityName - The name of the city to search images for.
     */
    const fetchImagesForCity = async (cityName) => {
      if (!cityName || !UNSPLASH_ACCESS_KEY || UNSPLASH_ACCESS_KEY === 'YOUR_UNSPLASH_ACCESS_KEY') {
        console.error('Unsplash API key is missing or invalid, or city name is empty.');
        cityImages.value = [];
        loadingImages.value = false;
        return;
      }

      loadingImages.value = true;
      cityImages.value = []; // Clear previous images
      currentImageIndex.value = 0; // Reset image index

      try {
        const response = await fetch(
          `https://api.unsplash.com/search/photos?query=${encodeURIComponent(cityName)}&client_id=${UNSPLASH_ACCESS_KEY}&per_page=15&orientation=landscape`
          // per_page=15 to get a decent number of images, orientation=landscape for better gallery display
        );

        if (!response.ok) {
          throw new Error(`Unsplash API HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.results && data.results.length > 0) {
          cityImages.value = data.results.map(photo => photo.urls.regular); // Using 'regular' size
        } else {
          message.info(`No images found for "${cityName}" on Unsplash.`);
        }
      } catch (error) {
        console.error('Error fetching images from Unsplash:', error);
        message.error('Failed to load images. Please check API key and network connection.');
      } finally {
        loadingImages.value = false;
      }
    };

    /**
     * Scrolls the image gallery to the currentImageIndex.
     */
    const scrollToCurrentImage = async () => {
      await nextTick(); // Ensure DOM is updated before attempting to scroll

      if (imageGalleryTrack.value && imageGalleryTrack.value.children.length > currentImageIndex.value) {
        const targetImage = imageGalleryTrack.value.children[currentImageIndex.value];
        // The parentElement of imageGalleryTrack is .image-gallery-display, which handles the scroll
        const scrollContainer = imageGalleryTrack.value.parentElement;
        
        // Calculate scrollLeft to center the target image
        const scrollLeft = targetImage.offsetLeft - (scrollContainer.offsetWidth - targetImage.offsetWidth) / 2;

        scrollContainer.scrollTo({
          left: scrollLeft,
          behavior: 'smooth'
        });
      }
    };

    /**
     * Navigates to the next image in the current city's gallery.
     */
    const nextImage = () => {
      if (currentImageIndex.value < cityImages.value.length - 1) {
        currentImageIndex.value++;
      }
    };

    /**
     * Navigates to the previous image in the current city's gallery.
     */
    const prevImage = () => {
      if (currentImageIndex.value > 0) {
        currentImageIndex.value--;
      }
    };

    /**
     * Navigates to the next city in the journey.
     */
    const nextCity = () => {
      if (currentCityIndex.value < journeyCities.value.length - 1) {
        currentCityIndex.value++;
      }
    };

    /**
     * Navigates to the previous city in the journey.
     */
    const prevCity = () => {
      if (currentCityIndex.value > 0) {
        currentCityIndex.value--;
      }
    };

    /**
     * Handles image loading errors, e.g., replacing with a placeholder.
     */
    const handleImageError = (event) => {
      event.target.src = 'https://placehold.co/600x400/cccccc/333333?text=Image+Not+Found'; // Placeholder
      event.target.alt = 'Image not found';
      console.warn('Failed to load image:', event.target.src);
    };

    // --- Watchers ---
    // Watch for changes in the current city (triggered by city navigation)
    watch(currentCity, (newCity) => {
      if (newCity) {
        fetchImagesForCity(newCity.city);
      } else {
        cityImages.value = [];
      }
    }, { immediate: true }); // Fetch images immediately when component mounts or journeyCities changes

    // Watch for changes in currentImageIndex to scroll the gallery
    watch(currentImageIndex, () => {
      scrollToCurrentImage();
    }, { flush: 'post' }); // 'post' ensures DOM updates before scrolling

    // Initial setup on mount
    onMounted(() => {
      if (journeyCities.value && journeyCities.value.length > 0) {
        // fetchImagesForCity is already triggered by currentCity watcher with immediate: true
      }
    });

    return {
      journeyCities,
      currentCityIndex,
      currentImageIndex,
      cityImages,
      loadingImages,
      currentCity,
      currentCityName,
      imageGalleryTrack, // Expose ref for template binding
      nextImage,
      prevImage,
      nextCity,
      prevCity,
      handleImageError,
      backgroundImageUrl,
    };
  }
});
</script>

<style scoped>
.city-image-gallery-container {
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

  /* Background image properties - for this component's background, allowing App.vue's fixed background to show */
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed; /* Ensures the background image stays fixed as content scrolls */
  /* Remove background-color here as it will be covered by the image */
}

.page-title {
  text-align: center;
  margin-bottom: 24px;
  color: #fff; /* White for better contrast on background image */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); /* Stronger shadow for readability */
}

.gallery-main-panel {
  position: relative; /* For absolute positioning of image nav buttons */
  width: 90%;
  height: 70vh; /* Set a fixed height for the main panel */
  max-width: 1200px;
  display: flex;
  flex-direction: column; /* Stack gallery and city nav vertically */
  
  /* Frosted glass effect properties */
  background-color: rgba(255, 255, 255, 0.2); /* Semi-transparent white */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  -webkit-backdrop-filter: blur(10px); /* For Safari support */
  border-radius: 12px; /* Rounded corners */
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); /* Subtle shadow */
  border: 1px solid rgba(255, 255, 255, 0.18); /* Light border */
  
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden; /* Hide overflow of images for horizontal scrolling */
}

.loading-overlay, .ant-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1; /* Make it fill available space */
  color: #333;
}

.image-gallery-display {
  flex-grow: 1; /* Allows gallery to take most space */
  display: flex;
  overflow-x: scroll; /* Enable horizontal scrolling */
  scroll-behavior: smooth; /* Smooth scrolling for image transitions */
  scrollbar-width: none; /* Hide scrollbar for Firefox */
  -ms-overflow-style: none; /* Hide scrollbar for IE/Edge */
  height: 100%; /* Fill parent height */
  width: 100%; /* Fill parent width */
}

/* Hide scrollbar for Chrome, Safari, Opera */
.image-gallery-display::-webkit-scrollbar {
  display: none;
}

.image-gallery-track {
  display: flex;
  align-items: center; /* Vertically center images */
  /* No transition here; scroll-behavior handles smooth scrolling of the container */
}

.gallery-image {
  height: 400px; /* Fixed height for all images */
  width: auto; /* Maintain aspect ratio */
  object-fit: contain; /* Ensure entire image is visible within bounds */
  flex-shrink: 0; /* Prevent images from shrinking */
  margin: 0 10px; /* Fixed horizontal spacing between images */
  border-radius: 8px; /* Slightly rounded corners for images */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Shadow for images */
  background-color: #f0f0f0; /* Placeholder background for images */
}

/* Image Navigation Buttons */
.nav-button.image-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 102; /* Higher than App.vue hotzones (100) and other content */
  width: 45px;
  height: 45px;
  font-size: 22px;
}
.nav-button.image-nav.left-nav {
  left: 0px; /* Position relative to .gallery-main-panel */
}
.nav-button.image-nav.right-nav {
  right: 0px; /* Position relative to .gallery-main-panel */
}

.city-navigation-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.3); /* Separator */
}

.city-info-display {
  margin-bottom: 16px;
  text-align: center;
}

.city-name-text {
  color: #333; /* Darker text for readability */
  margin-bottom: 0 !important; /* Override Ant Design default margin */
}

.city-nav-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  width: 100%;
}

.city-nav-buttons .ant-btn {
  flex: 1;
  max-width: 200px;
  height: 48px;
  font-size: 1.1em;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .gallery-main-panel {
    height: 60vh;
    padding: 16px;
  }
  .gallery-image {
    height: 250px; /* Smaller height on mobile */
  }
  .nav-button.image-nav {
    width: 35px;
    height: 35px;
    font-size: 18px;
  }
  .city-nav-buttons {
    flex-direction: column;
  }
  .city-nav-buttons .ant-btn {
    max-width: 100%;
  }
  .page-title {
    font-size: 1.8em;
    margin-bottom: 16px;
  }
}
</style>
