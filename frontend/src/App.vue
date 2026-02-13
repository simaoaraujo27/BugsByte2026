<script setup>
import { ref } from 'vue';
import LoginPage from './components/LoginPage.vue';
import LandingPage from './components/LandingPage.vue';

const currentView = ref('landing');
</script>

<template>
  <component 
    :is="currentView === 'login' ? LoginPage : LandingPage" 
    @navigate="currentView = $event" 
  />
</template>

<style>
/* Reset some default styles to let Tailwind take over */
body {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
}
#app {
  width: 100%;
  height: 100%;
  max-width: none;
  padding: 0;
  margin: 0;
  display: block;
}
</style>
