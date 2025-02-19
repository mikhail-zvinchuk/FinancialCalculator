<template>
  <v-layout>
    <v-navigation-drawer
      location="left"
      permanent
      width="400"
      class="parameters-drawer"
    >
      <v-card flat class="h-100">
        <v-card-title class="text-h6 py-4 bg-grey-darken-3 text-white">
          Parameters
        </v-card-title>
        <v-card-text class="pa-4">
          <ChartParametersForm @update-params="updateChart" />
        </v-card-text>
      </v-card>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid class="pa-6">
        <v-card class="h-100">
          <v-card-text>
            <div v-if="error" class="error-message mb-4">
              <v-alert type="error" :text="error" />
            </div>

            <div v-if="isLoading" class="d-flex justify-center align-center" style="height: 400px;">
              <v-progress-circular indeterminate color="primary" size="64" />
            </div>

            <div v-if="hasValidData" id="chart">
              <apexchart
                ref="chartRef"
                type="scatter"
                height="500"
                :options="chartOptions"
                :series="series"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { useChartDataStore } from '@/stores/chartData'
import { storeToRefs } from 'pinia'
import type { ApexOptions } from 'apexcharts'
import type { MortgageToInvestmentRequest } from '@/stores/chartData'
import ChartParametersForm from './ChartParametersForm.vue'

const store = useChartDataStore()
const { series, dataLoaded, error } = storeToRefs(store)
const isLoading = computed(() => store.isLoading)
const hasValidData = computed(() => dataLoaded.value && series.value.length > 0)
const chartRef = ref(null)

const updateChart = async (params: MortgageToInvestmentRequest) => {
  if (!params?.investmentInput?.initialSum ||
      !params?.investmentInput?.investmentRate ||
      !params?.investmentInput?.returnRate ||
      !params?.mortgageInput?.initialPrice ||
      !params?.mortgageInput?.growthRate ||
      !params?.mortgageInput?.downPaymentPercentage) {
    store.error = "Invalid parameters provided"
    return
  }

  try {
    await store.fetchChartData(params)
  } catch (err) {
    store.error = err instanceof Error ? err.message : 'Failed to update chart'
  }
}

// Load initial data
onMounted(async () => {
  try {
    await store.fetchInitialData()
  } catch (err) {
    store.error = err instanceof Error ? err.message : 'Failed to load initial data'
  }
})

// Register components
const components = {
  apexchart: VueApexCharts,
  ChartParametersForm
}

// Chart options using ref for reactivity
const chartOptions = ref<ApexOptions>({
  chart: {
    type: 'scatter',
    id: 'investment-mortgage-chart',
    toolbar: {
      show: true,
      tools: {
        download: true,
        selection: true,
        zoom: true,
        zoomin: true,
        zoomout: true,
        pan: true,
        reset: true
      },
      autoSelected: 'zoom'
    },
    zoom: {
      enabled: true,
      type: 'xy',
      autoScaleYaxis: true
    }
  },
  markers: {
    size: 6,
    strokeWidth: 1,
    hover: {
      size: 8
    }
  },
  dataLabels: {
    enabled: false
  },
  grid: {
    xaxis: {
      lines: {
        show: true
      }
    },
    yaxis: {
      lines: {
        show: true
      }
    }
  },
  colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0'],
  title: {
    text: 'Property Value Over Time',
    align: 'left',
    style: {
      fontSize: '18px',
      fontWeight: 600
    }
  },
  xaxis: {
    type: 'numeric',
    title: {
      text: 'Years',
      style: {
        fontSize: '14px',
        fontWeight: 500
      }
    },
    labels: {
      formatter: (value: string) => `Year ${Math.round(Number(value))}`,
      style: {
        fontSize: '12px'
      }
    },
    min: 0,
    max: 20,
    tickAmount: 10
  },
  yaxis: [{
    title: {
      text: 'Property Value ($)',
      style: {
        fontSize: '14px',
        fontWeight: 500
      }
    },
    labels: {
      formatter: (value: number) => `$${value.toLocaleString()}`,
      style: {
        fontSize: '12px'
      }
    },
    min: 450000,
    max: 550000,
    tickAmount: 8,
    forceNiceScale: true
  }],
  tooltip: {
    shared: false,
    intersect: true,
    x: {
      show: true,
      formatter: (value: number) => `Year ${Math.round(value)}`
    },
    y: {
      formatter: (value: number) => `$${value.toLocaleString()}`
    }
  }
})
</script>

<style scoped>
.error-message {
  max-width: 600px;
  margin: 0 auto;
}

.h-100 {
  height: 100%;
}

.v-card {
  display: flex;
  flex-direction: column;
}

.v-card-text {
  flex: 1;
  overflow: auto;
}

.parameters-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.parameters-drawer :deep(.v-navigation-drawer__content) {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

#chart {
  padding: 1rem;
  min-height: 400px;
}
</style>
