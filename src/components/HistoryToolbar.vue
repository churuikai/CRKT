<template>
  <div
    class="flex items-center gap-1 px-3 py-1.5 bg-white border-b border-gray-200 select-none"
  >
    <button
      class="px-2 py-0.5 text-sm border border-gray-300 rounded hover:bg-gray-100 active:bg-gray-200"
      title="上翻历史记录"
      @click="$emit('navigate-up')"
    >
      ↑
    </button>
    <button
      class="px-2 py-0.5 text-sm border border-gray-300 rounded hover:bg-gray-100 active:bg-gray-200"
      title="下翻历史记录"
      @click="$emit('navigate-down')"
    >
      ↓
    </button>
    <span v-if="inHistoryMode" class="text-xs text-gray-500 ml-1">
      上{{ historyIndex + 1 }}条
    </span>
    <div class="flex-1" />
    <span v-if="isTranslating" class="text-xs text-purple-500">翻译中...</span>
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
