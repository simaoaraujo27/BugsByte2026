<script setup>
import { ref, onMounted } from 'vue';

const items = ref([]);

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/items/');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    items.value = await response.json();
  } catch (error) {
    console.error('Error fetching items:', error);
  }
});
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />
    <div class="wrapper">
      <h1>Vue.js Frontend with FastAPI Backend</h1>
    </div>
  </header>

  <main>
    <h2>Items from Backend:</h2>
    <p v-if="items.length === 0">No items found. Try adding some via the backend API.</p>
    <ul>
      <li v-for="item in items" :key="item.id">
        <strong>{{ item.name }}</strong>: {{ item.description }} (ID: {{ item.id }})
      </li>
    </ul>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
