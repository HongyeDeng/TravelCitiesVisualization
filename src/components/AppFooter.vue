<template>
  <footer class="app-footer-container">
    <a-row :gutter="[16, 16]" class="footer-content-row">
      <!-- Left 2/3: Vivid Text -->
      <a-col :xs="24" :md="16" class="footer-text-col">
        <div class="vivid-text-wrapper">
          <span class="vivid-word vivid-start">Start</span>
          <span class="vivid-word vivid-your">Your</span>
          <span class="vivid-word vivid-trip">Trip</span>
        </div>
      </a-col>

      <!-- Right 1/3: GitHub Link -->
      <a-col :xs="24" :md="8" class="footer-github-col">
        <a href="https://github.com/HongyeDeng?tab=stars" target="_blank" rel="noopener noreferrer" class="github-link">
          <GithubOutlined class="github-icon" />
          <span class="github-text">Visit our GitHub</span>
        </a>
      </a-col>
    </a-row>
  </footer>
</template>

<script>
import { defineComponent } from 'vue';
import { Row, Col, Typography } from 'ant-design-vue';
import { GithubOutlined } from '@ant-design/icons-vue';

export default defineComponent({
  name: 'AppFooter',
  components: {
    'a-row': Row,
    'a-col': Col,
    //'a-typography-text': Typography.Text, // Only need Typography.Text for simple text
    //#'a-typography-title': Typography.Title, // For the main title
    GithubOutlined,
  },
  setup() {
    return {};
  }
});
</script>

<style scoped>
.app-footer-container {
  width: 100%;
  padding: 40px 24px; /* Adjust padding as needed */
  background-color: #2c3e50; /* Dark background for footer */
  color: #ecf0f1; /* Light text color */
  box-sizing: border-box;
  display: flex; /* Use flex to center content */
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1); /* Subtle top border */
}

.footer-content-row {
  width: 100%;
  max-width: 1200px; /* Max width for content consistency */
  display: flex; /* Ensure it's a flex container for columns */
  align-items: center; /* Vertically align items in the row */
}

.footer-text-col {
  text-align: center; /* Center text on mobile by default */
  margin-bottom: 20px; /* Space below text on mobile */
}

@media (min-width: 768px) {
  .footer-text-col {
    text-align: left; /* Align text to left on larger screens */
    margin-bottom: 0;
  }
}

.vivid-text-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center words vertically */
  font-weight: bold;
}

@media (min-width: 768px) {
  .vivid-text-wrapper {
    align-items: flex-start; /* Align words to left on larger screens */
  }
}

.vivid-word {
  display: block; /* Each word on its own line */
  text-transform: uppercase;
  font-family: 'Montserrat', sans-serif; /* Example font */
  padding: 5px 0;
  transition: all 0.3s ease; /* Smooth transition for hover effects */
}

.vivid-start {
  font-size: 3.5em; /* Larger size for 'Start' */
  color: #1890ff; /* Ant Design blue */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  transform: rotate(-3deg); /* Slight rotation */
}

.vivid-your {
  font-size: 2.2em; /* Medium size for 'Your' */
  color: #52c41a; /* Ant Design green */
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.4);
  transform: rotate(2deg); /* Slight rotation */
}

.vivid-trip {
  font-size: 4em; /* Largest size for 'Trip' */
  color: #faad14; /* Ant Design gold */
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.6);
  transform: rotate(-5deg); /* More rotation */
}

.vivid-word:hover {
  transform: scale(1.05); /* Slight zoom on hover */
  color: #fff; /* White on hover for emphasis */
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
}


.footer-github-col {
  text-align: center; /* Center link on mobile */
}

@media (min-width: 768px) {
  .footer-github-col {
    text-align: right; /* Align link to right on larger screens */
  }
}

.github-link {
  display: inline-flex; /* Align icon and text horizontally */
  align-items: center;
  gap: 10px; /* Space between icon and text */
  color: #ecf0f1; /* Light color for link */
  font-size: 1.2em;
  text-decoration: none;
  transition: color 0.3s ease;
}

.github-link:hover {
  color: #1890ff; /* Blue on hover */
  text-decoration: underline;
}

.github-icon {
  font-size: 2em; /* Size of the GitHub icon */
  transition: transform 0.3s ease;
}

.github-link:hover .github-icon {
  transform: rotate(10deg) scale(1.1); /* Rotate and scale icon on hover */
}

/* Responsive adjustments for columns */
@media (max-width: 767px) {
  .footer-text-col,
  .footer-github-col {
    flex: 0 0 100%; /* Make them full width on small screens */
    max-width: 100%;
  }

  .footer-text-col {
    order: 2; /* Put text below link on mobile */
  }
  .footer-github-col {
    order: 1; /* Put link above text on mobile */
    margin-bottom: 20px; /* Space between link and text on mobile */
  }
}
</style>
