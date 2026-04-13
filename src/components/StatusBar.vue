<template>
  <div
    class="flex items-center justify-between px-3 py-1 bg-gray-100 border-t border-gray-200 text-xs text-gray-500"
  >
    <span>CRKT Translator</span>
    <span v-if="model">{{ model }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ model?: string }>();
</script>
