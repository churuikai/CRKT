<template>
  <div class="flex-1 overflow-auto px-5 py-4">
    <div v-if="isTranslating && !content" class="flex items-center gap-2 text-gray-400 text-sm">
      <span class="inline-block w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
      翻译中...
    </div>
    <div v-else-if="error" class="text-red-500/80 text-sm">
      {{ error }}
    </div>
    <div
      v-else-if="content"
      class="prose prose-sm prose-gray max-w-none
        prose-headings:font-semibold prose-headings:text-gray-800
        prose-p:text-gray-700 prose-p:leading-relaxed
        prose-code:text-[13px] prose-code:bg-black/[0.04] prose-code:px-1 prose-code:py-0.5 prose-code:rounded
        prose-pre:bg-gray-800 prose-pre:text-gray-100 prose-pre:rounded-lg"
      v-html="renderedHtml"
    />
    <div v-else class="text-gray-300 text-sm">
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
