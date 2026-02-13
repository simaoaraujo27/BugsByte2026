<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  },
  active: {
    type: Boolean,
    default: false
  },
  highlight: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select'])
</script>

<template>
  <button
    type="button"
    class="menu-item"
    :class="{ active, highlight }"
    @click="$emit('select')"
  >
    <span v-if="icon" class="item-icon" aria-hidden="true">{{ icon }}</span>
    <span class="item-label">{{ label }}</span>
  </button>
</template>

<style scoped>
.menu-item {
  border: 0;
  border-radius: 10px;
  padding: 10px 12px;
  text-align: left;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.menu-item:hover {
  background: var(--menu-hover-bg);
  color: var(--text-main);
  transform: translateX(2px);
}

.menu-item.active {
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
}

.menu-item.highlight {
  background: var(--menu-highlight-bg);
  color: var(--menu-highlight-text);
  font-weight: 700;
}

.menu-item.highlight:hover {
  background: var(--menu-highlight-hover-bg);
}

.menu-item.highlight.active {
  background: var(--menu-highlight-active-bg);
  color: var(--menu-highlight-active-text);
}

.item-icon {
  font-size: 1rem;
  line-height: 1;
}

.item-label {
  white-space: nowrap;
}
</style>
