<template>
  <v-form @submit.prevent="submitForm" ref="form" class="pa-2 bg-dark">
    <v-container class="pa-0">
      <div class="bg-grey-darken-4 rounded pa-2 mb-3">
        <h3 class="text-subtitle-1 text-grey-lighten-1 mb-0">Investment Parameters</h3>
      </div>
      <v-row no-gutters class="mb-2 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Initial Investment:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.investmentInput.initialSum"
            type="number"
            prefix="$"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[v => !!v || 'Required', v => v > 0 || 'Must be greater than 0']"
            required
          />
        </v-col>
      </v-row>
      <v-row no-gutters class="mb-2 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Investment Rate:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.investmentInput.investmentRate"
            type="number"
            suffix="%"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[v => !!v || 'Required', v => v >= 0 || 'Must be positive']"
            required
          />
        </v-col>
      </v-row>
      <v-row no-gutters class="mb-4 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Return Rate:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.investmentInput.returnRate"
            type="number"
            suffix="%"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[v => !!v || 'Required', v => v >= 0 || 'Must be positive']"
            required
          />
        </v-col>
      </v-row>

      <div class="bg-grey-darken-4 rounded pa-2 mb-3">
        <h3 class="text-subtitle-1 text-grey-lighten-1 mb-0">Mortgage Parameters</h3>
      </div>
      <v-row no-gutters class="mb-2 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Initial Property Price:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.mortgageInput.initialPrice"
            type="number"
            prefix="$"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[v => !!v || 'Required', v => v > 0 || 'Must be greater than 0']"
            required
          />
        </v-col>
      </v-row>
      <v-row no-gutters class="mb-2 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Property Growth Rate:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.mortgageInput.growthRate"
            type="number"
            suffix="%"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[v => !!v || 'Required', v => v >= 0 || 'Must be positive']"
            required
          />
        </v-col>
      </v-row>
      <v-row no-gutters class="mb-4 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Down Payment:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.mortgageInput.downPaymentPercentage"
            type="number"
            suffix="%"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[
              v => !!v || 'Required',
              v => v > 0 || 'Must be greater than 0',
              v => v <= 100 || 'Must be less than or equal to 100'
            ]"
            required
          />
        </v-col>
      </v-row>

      <v-row no-gutters class="mb-4 align-center">
        <v-col cols="5" class="pr-2 text-grey-lighten-1">Purchase Year:</v-col>
        <v-col>
          <v-text-field
            v-model.number="params.purchaseX"
            type="number"
            density="compact"
            hide-details
            color="primary"
            bg-color="grey-darken-3"
            theme="dark"
            :rules="[v => !v || v >= 0 || 'Must be positive']"
          />
        </v-col>
      </v-row>

      <v-btn
        color="grey-darken-3"
        type="submit"
        :loading="loading"
        :disabled="loading"
        class="mb-2 text-grey-lighten-1"
        block
        theme="dark"
      >
        Calculate
      </v-btn>
    </v-container>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import type { MortgageToInvestmentRequest } from '@/stores/chartData'

export default defineComponent({
  name: 'ChartParametersForm',

  emits: ['update-params'],

  setup(_, { emit }) {
    const loading = ref(false)
    const formValid = ref(true)
    const form = ref<any>(null)

    const params = ref<MortgageToInvestmentRequest>({
      investmentInput: {
        initialSum: 100000,
        investmentRate: 10,     // Will be converted to 0.1
        returnRate: 7           // Will be converted to 0.07
      },
      mortgageInput: {
        initialPrice: 500000,
        growthRate: 3,          // Will be converted to 0.03
        downPaymentPercentage: 20  // Will be converted to 0.2
      }
    })

    const validateParams = (params: MortgageToInvestmentRequest): boolean => {
      const investment = params.investmentInput
      const mortgage = params.mortgageInput

      return !!(investment?.initialSum &&
                investment?.investmentRate &&
                investment?.returnRate &&
                mortgage?.initialPrice &&
                mortgage?.growthRate &&
                mortgage?.downPaymentPercentage)
    }

    const submitForm = async (event: Event) => {
      event.preventDefault() // Prevent form submission

      if (loading.value) return // Prevent multiple submissions

      loading.value = true
      try {
        // Validate all required fields have values
        if (!validateParams(params.value)) {
          console.error('Parameter validation failed:', params.value)
          formValid.value = false
          return
        }
        formValid.value = true

        // Convert percentage values to decimals and ensure all values are numbers
        const formattedParams: MortgageToInvestmentRequest = {
          investmentInput: {
            initialSum: Number(params.value.investmentInput.initialSum),
            investmentRate: Number(params.value.investmentInput.investmentRate),  // Keep as percentage
            returnRate: Number(params.value.investmentInput.returnRate)  // Keep as percentage
          },
          mortgageInput: {
            initialPrice: Number(params.value.mortgageInput.initialPrice),
            growthRate: Number(params.value.mortgageInput.growthRate),  // Keep as percentage
            downPaymentPercentage: Number(params.value.mortgageInput.downPaymentPercentage)  // Keep as percentage
          }
        }

        // Only add purchaseX if it has a valid value
        if (params.value.purchaseX !== undefined && params.value.purchaseX >= 0) {
          formattedParams.purchaseX = Number(params.value.purchaseX)
        }

        console.log('Submitting parameters:', formattedParams)
        emit('update-params', formattedParams)
      } catch (err) {
        console.error('Error submitting form:', err)
      } finally {
        loading.value = false
      }
    }

    // Submit form with initial values after a short delay to ensure component is fully mounted
    onMounted(() => {
      setTimeout(() => {
        if (validateParams(params.value)) {
          console.log('Submitting initial parameters on mount')
          submitForm(new Event('submit'))
        }
      }, 100)
    })

    return {
      form,
      params,
      loading,
      formValid,
      submitForm
    }
  }
})
</script>
