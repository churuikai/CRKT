<template>
  <div class="flex-1 overflow-auto p-4">
    <div v-if="isTranslating && !content" class="text-purple-600 text-lg">
      翻译中...
    </div>
    <div v-else-if="error" class="text-red-500">
      {{ error }}
    </div>
    <div
      v-else-if="content"
      class="prose prose-sm max-w-none"
      v-html="renderedHtml"
    />
    <div v-else class="text-gray-400 text-sm">
      选中文本后按快捷键开始翻译
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { renderMarkdown } from "../lib/markdown";

const props = defineProps<{
  content: string;
  isTranslating: boolean;
  error: string;
}>();

const renderedHtml = computed(() => renderMarkdown(props.content));
</script>
