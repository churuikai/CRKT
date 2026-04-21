<template>
  <div
    class="flex items-center gap-1.5 px-3 py-1.5 border-b border-black/5 select-none"
  >
    <button
      class="w-6 h-6 flex items-center justify-center text-xs text-gray-500 rounded-md hover:bg-black/5 active:bg-black/10 transition-colors"
      title="上翻历史记录"
      @click="$emit('navigate-up')"
    >
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 7.5L6 4L9.5 7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </button>
    <button
      class="w-6 h-6 flex items-center justify-center text-xs text-gray-500 rounded-md hover:bg-black/5 active:bg-black/10 transition-colors"
      title="下翻历史记录"
      @click="$emit('navigate-down')"
    >
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </button>
    <span v-if="inHistoryMode" class="text-[11px] text-gray-400 ml-0.5 tabular-nums">
      {{ historyIndex + 1 }}
    </span>
    <div class="flex-1" />
    <div v-if="isTranslating" class="flex items-center gap-1.5">
      <span class="inline-block w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
      <span class="text-[11px] text-gray-400">翻译中</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  inHistoryMode: boolean;
  historyIndex: number;
  isTranslating: boolean;
}>();
defineEmits<{
  "navigate-up": [];
  "navigate-down": [];
}>();
</script>
