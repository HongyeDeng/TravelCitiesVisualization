// src/stores/journey.ts
import { defineStore } from 'pinia';

// Define the comprehensive shape of a city object for our journey
export interface JourneyCity {
  id: string; // Unique ID from your backend data
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  budget_level: string; // Added budget_level
  culture: number;      // Added all rating properties
  adventure: number;
  nature: number;
  beaches: number;
  nightlife: number;
  cuisine: number;
  wellness: number;
  urban: number;
  seclusion: number;
  // Add any other properties you might need from the city object here
}

export const useJourneyStore = defineStore('journey', {
  state: () => ({
    selectedJourneyCities: [] as JourneyCity[], // Array to hold cities in the journey
  }),
  actions: {
    /**
     * Adds a city to the journey if it's not already present.
     * Ensure the city object contains all required properties from the backend.
     * @param {JourneyCity} city - The city object to add.
     */
    addCity(city: JourneyCity) {
      if (!this.selectedJourneyCities.some(c => c.id === city.id)) {
        // Ensure all properties are present, even if undefined in source (coalesce to 0 or default)
        const cityToAdd: JourneyCity = {
          id: city.id,
          city: city.city,
          country: city.country,
          latitude: city.latitude,
          longitude: city.longitude,
          budget_level: city.budget_level || 'N/A', // Provide a default if missing
          culture: city.culture || 0,
          adventure: city.adventure || 0,
          nature: city.nature || 0,
          beaches: city.beaches || 0,
          nightlife: city.nightlife || 0,
          cuisine: city.cuisine || 0,
          wellness: city.wellness || 0,
          urban: city.urban || 0,
          seclusion: city.seclusion || 0,
        };
        this.selectedJourneyCities.push(cityToAdd);
        console.log(`Added ${city.city} to journey.`);
      } else {
        console.log(`${city.city} is already in the journey.`);
      }
    },
    /**
     * Removes a city from the journey by its ID.
     * @param {string} cityId - The ID of the city to remove.
     */
    removeCity(cityId: string) {
      const initialLength = this.selectedJourneyCities.length;
      this.selectedJourneyCities = this.selectedJourneyCities.filter(city => city.id !== cityId);
      if (this.selectedJourneyCities.length < initialLength) {
        console.log(`Removed city with ID ${cityId} from journey.`);
      } else {
        console.log(`City with ID ${cityId} not found in journey.`);
      }
    },
    /**
     * Sets the entire journey cities array. Useful for loading saved journeys.
     * @param {JourneyCity[]} cities - An array of city objects.
     */
    setJourneyCities(cities: JourneyCity[]) {
      this.selectedJourneyCities = cities;
      console.log('Journey cities updated.');
    },
    /**
     * Clears all cities from the journey.
     */
    clearJourney() {
      this.selectedJourneyCities = [];
      console.log('Journey cleared.');
    },
    /**
     * Confirms the current journey route and returns the list of city names.
     * In a real application, this might trigger a save to a backend.
     * @returns {string[]} An array of city names in the confirmed journey.
     */
    confirmJourneyRoute(): string[] {
      const cityNames = this.selectedJourneyCities.map(city => city.city);
      console.log('Confirmed Journey Route:', cityNames);
      // You would typically send this `cityNames` or `selectedJourneyCities` array to your backend here
      return cityNames;
    }
  },
  getters: {
    /**
     * Returns the full array of selected journey city objects.
     * @returns {JourneyCity[]} The array of journey cities.
     */
    getJourneyCities(): JourneyCity[] {
      return this.selectedJourneyCities;
    },
    /**
     * Returns an array of IDs of cities in the journey.
     * @returns {string[]} The array of journey city IDs.
     */
    getJourneyCityIds(): string[] {
      return this.selectedJourneyCities.map(city => city.id);
    },
    /**
     * Returns the geographical coordinates (lat/lon) of cities in the journey, in order.
     * Useful for drawing polyline on map.
     * @returns {number[][]} An array of [latitude, longitude] pairs.
     */
    getJourneyCoordinates(): number[][] {
        return this.selectedJourneyCities.map(city => [city.latitude, city.longitude]);
    }
  },
});
