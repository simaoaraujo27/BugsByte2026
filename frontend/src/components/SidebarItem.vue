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
  --text-main: #11263f;
  --text-muted: #54667e;
  --accent-soft: #e3f7f2;

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
  background: #f3f7fb;
  color: var(--text-main);
  transform: translateX(2px);
}

.menu-item.active {
  background: var(--accent-soft);
  color: #0a705d;
}

.menu-item.highlight {
  background: #fff1e7;
  color: #9a3412;
  font-weight: 700;
}

.menu-item.highlight:hover {
  background: #ffe5d2;
}

.menu-item.highlight.active {
  background: #ffd9bd;
  color: #7c2d12;
}

.item-icon {
  font-size: 1rem;
  line-height: 1;
}

.item-label {
  white-space: nowrap;
}
</style>
