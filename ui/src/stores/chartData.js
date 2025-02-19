import { defineStore } from 'pinia'
import axios from 'axios'

export const useChartDataStore = defineStore('chartData', {
  state: () => ({
    series: [],
    dataLoaded: false,
    error: null
  }),

  actions: {
    async fetchChartData() {
      try {
        this.error = null
        const response = await axios.get('/data')
        this.series = [{
          data: response.data.series
        }]
        this.dataLoaded = true
      } catch (error) {
        console.error('Error fetching chart data:', error)
        this.error = error.message
      }
    }
  },

  getters: {
    isLoading: (state) => !state.dataLoaded && !state.error,
    hasError: (state) => !!state.error
  }
})
