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
  border-radius: 12px;
  padding: 12px 16px;
  text-align: left;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-width: 0;
}

.menu-item:hover {
  background: var(--menu-hover-bg);
  color: var(--text-main);
  transform: translateX(4px);
}

.menu-item.active {
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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
  box-shadow: 0 4px 12px rgba(154, 52, 18, 0.1);
}

.item-icon {
  font-size: 1.25rem;
  line-height: 1;
}

.item-label {
  white-space: normal;
  overflow-wrap: anywhere;
  line-height: 1.2;
}
</style>
