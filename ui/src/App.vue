<script setup>
import SideBar from "./components/SideBar.vue"
import TopBar from "./components/TopBar.vue"
</script>

<template>
  <VApp>
    <v-layout class="rounded rounded-md">
      <SideBar />


      <v-main class="d-flex align-center justify-center" style="min-height: 300px;">
        Main Content
      </v-main>
    </v-layout>
  </VApp>
</template>
