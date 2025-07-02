<template>
  <div class="homepage-container">
    <div class="hero-section">
      <img src="/images/Cover.jpg" alt="Discover Cities" class="hero-image" />
      <div class="hero-overlay">
        <h1>Unlock the World</h1>
        <a-button type="primary" size="large" @click="emitScrollToRegions" class="scroll-button">
          Explore Now
        </a-button>
      </div>
    </div>
  </div>
</template>

<script>
import { Button } from 'ant-design-vue'; // Import the Button component

export default {
  name: 'HomePage',
  components: {
    'a-button': Button, // Register the Ant Design Button
  },
  emits: ['scroll-to-regions'],
  setup(props, { emit }) {
    /**
     * Emits an event to signal that the page should scroll to the regions section.
     */
    const emitScrollToRegions = () => {
      emit('scroll-to-regions');
    };

    return {
      emitScrollToRegions
    };
  }
}
</script>

<style scoped>
.homepage-container {
  width: 100%;
  overflow-x: hidden;
}

.hero-section {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  z-index: -1;
}

.hero-overlay {
  text-align: center;
  color: white;
  z-index: 1;
  background-color: rgba(0, 0, 0, 0.4);
  padding: 30px;
  border-radius: 10px;
}

.hero-overlay h1 {
  font-size: 5em;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

/* No specific styling needed for .scroll-button now, as Ant Design handles its appearance */
/* If you need to override Ant Design's default styles, you'd add them here,
   but for primary/large button, it often looks good out of the box. */

.next-content-section {
  min-height: 100vh;
  padding: 50px 20px;
  background-color: #f8f8f8;
  text-align: center;
}

/* Ensure Ant Design's global styles are loaded. This is usually done in main.js */
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
</style>