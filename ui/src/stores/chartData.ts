import { defineStore } from 'pinia'
import axios from 'axios'

interface DataPoint {
  x: number | Date
  y: number
}

interface SeriesData {
  data: DataPoint[]
}

interface ChartState {
  series: SeriesData[]
  dataLoaded: boolean
  error: string | null
}

interface ApiResponse {
  series: DataPoint[]
}

export const useChartDataStore = defineStore('chartData', {
  state: (): ChartState => ({
    series: [],
    dataLoaded: false,
    error: null
  }),

  actions: {
    async fetchChartData(): Promise<void> {
      try {
        this.error = null
        const response = await axios.get<ApiResponse>('/data')
        this.series = [{
          data: response.data.series
        }]
        this.dataLoaded = true
      } catch (error) {
        console.error('Error fetching chart data:', error)
        this.error = error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  },

  getters: {
    isLoading: (state: ChartState): boolean => !state.dataLoaded && !state.error,
    hasError: (state: ChartState): boolean => !!state.error
  }
})
