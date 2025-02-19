import { defineStore } from 'pinia'
import api from '@/api/config'

// API Interfaces based on OpenAPI spec
export interface Point {
  x: number
  y: number
}

export interface PlotMetadata {
  identifier: string
  points: Point[]
}

export interface InvestmentCurve {
  initialSum: number
  investmentRate: number
  returnRate: number
}

export interface RealEstateMortgageGrowth {
  initialPrice: number
  growthRate: number
  downPaymentPercentage: number
}

export interface MortgageToInvestmentRequest {
  investmentInput: InvestmentCurve
  mortgageInput: RealEstateMortgageGrowth
  purchaseX?: number
}

interface DataResponse {
  series: PlotMetadata[]
  error?: string
}

interface ChartState {
  series: {
    data: Point[]
    name: string
    type?: string
  }[]
  dataLoaded: boolean
  error: string | null
}

export const useChartDataStore = defineStore('chartData', {
  state: (): ChartState => ({
    series: [],
    dataLoaded: false,  // Start with false to show loading state
    error: null
  }),

  actions: {
    async fetchInitialData(): Promise<void> {
      try {
        this.error = null
        this.dataLoaded = false
        this.series = [] // Clear existing data

        // Use default values for initial data
        const defaultParams = {
          investmentInput: {
            initialSum: 100000,
            investmentRate: 0.10,  // 10%
            returnRate: 0.07  // 7%
          },
          mortgageInput: {
            initialPrice: 500000,
            growthRate: 0.03,  // 3%
            downPaymentPercentage: 0.20  // 20%
          }
        }

        console.log('Fetching initial data with default params:', defaultParams)
        const response = await api.post<DataResponse>('/data', defaultParams)

        if (response.data.error) {
          throw new Error(response.data.error)
        }

        this.processResponse(response.data)
      } catch (error) {
        console.error('Error fetching initial data:', error)
        this.error = error instanceof Error ? error.message : 'Unknown error occurred'
        this.dataLoaded = false
        this.series = []
      }
    },

    async fetchChartData(params: MortgageToInvestmentRequest): Promise<void> {
      try {
        this.error = null
        this.dataLoaded = false
        this.series = [] // Clear existing data

        // Validate parameters
        if (!params?.investmentInput?.initialSum ||
            !params?.investmentInput?.investmentRate ||
            !params?.investmentInput?.returnRate ||
            !params?.mortgageInput?.initialPrice ||
            !params?.mortgageInput?.growthRate ||
            !params?.mortgageInput?.downPaymentPercentage) {
          console.error('Missing or invalid parameters:', params)
          this.error = "Missing required parameters"
          this.dataLoaded = true
          return
        }

        // Prepare the request payload
        const requestData = {
          investmentInput: {
            initialSum: Number(params.investmentInput.initialSum),
            investmentRate: Number(params.investmentInput.investmentRate) / 100,  // Convert to decimal
            returnRate: Number(params.investmentInput.returnRate) / 100  // Convert to decimal
          },
          mortgageInput: {
            initialPrice: Number(params.mortgageInput.initialPrice),
            growthRate: Number(params.mortgageInput.growthRate) / 100,  // Convert to decimal
            downPaymentPercentage: Number(params.mortgageInput.downPaymentPercentage) / 100  // Convert to decimal
          }
        }

        // Add optional purchaseX if present
        if (params.purchaseX !== undefined && params.purchaseX >= 0) {
          requestData['purchaseX'] = Number(params.purchaseX)
        }

        console.log('Sending request with data:', requestData)
        const response = await api.post<DataResponse>('/data', requestData)

        if (response.data.error) {
          throw new Error(response.data.error)
        }

        this.processResponse(response.data)
      } catch (error) {
        console.error('Error fetching chart data:', error)
        this.error = error instanceof Error ? error.message : 'Unknown error occurred'
        this.dataLoaded = false
        this.series = []
      }
    },

    processResponse(data: DataResponse): void {
      if (!data.series || !Array.isArray(data.series)) {
        throw new Error('Invalid response format: missing or invalid series data')
      }

      // Transform the API response into the format expected by ApexCharts
      this.series = data.series.map(graph => {
        // Format the identifier for better display
        const formatIdentifier = (id: string) => {
          switch (id.toLowerCase()) {
            case 'investment_value':
              return 'Investment Growth'
            case 'property_value':
              return 'Property Value'
            case 'mortgage_remaining':
              return 'Remaining Mortgage'
            case 'equity_value':
              return 'Home Equity'
            case 'realestatepricegrowth':
              return 'Real Estate Price Growth'
            default:
              return id.split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ')
          }
        }

        const name = formatIdentifier(graph.identifier)

        // Extract points from the graph data
        if (!Array.isArray(graph.points)) {
          throw new Error(`Invalid points data for series "${name}"`)
        }

        // Format the data points for ApexCharts
        const formattedData = graph.points
          .map(point => {
            if (!point || typeof point.x !== 'number' || typeof point.y !== 'number') {
              return null
            }
            return {
              x: point.y,  // Years on x-axis
              y: point.x   // Property values on y-axis
            }
          })
          .filter(point => point !== null)
          .sort((a, b) => a.x - b.x)  // Sort by year (x-axis)

        if (formattedData.length === 0) {
          throw new Error(`No valid points found for series "${name}"`)
        }

        return {
          name,
          type: 'scatter',
          data: formattedData
        }
      })

      if (this.series.length === 0) {
        throw new Error('No valid series data found in response')
      }

      this.dataLoaded = true
    }
  },

  getters: {
    isLoading: (state: ChartState): boolean => !state.dataLoaded && !state.error,
    hasError: (state: ChartState): boolean => !!state.error,
    getSeriesData: (state: ChartState) => state.series
  }
})
