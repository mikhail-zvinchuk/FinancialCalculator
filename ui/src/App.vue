<script setup>
import SideBar from "./components/SideBar.vue"
import TopBar from "./components/TopBar.vue"
import ChartComponent from "./components/ChartComponent.vue"
</script>

<template>
  <VApp>
    <v-layout class="rounded rounded-md">
      <SideBar />


      <v-main class="d-flex align-center justify-center" style="min-height: 300px;">
        <ChartComponent />
      </v-main>
    </v-layout>
  </VApp>
</template>
