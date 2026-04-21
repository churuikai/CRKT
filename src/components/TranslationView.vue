<template>
  <div class="overflow-auto px-5 py-4">
    <!-- Loading without content yet -->
    <div v-if="isTranslating && !content" class="flex items-center gap-1.5 text-[13px] text-gray-400/80 pt-1">
      <span class="text-gray-400/70">翻译中</span>
      <span class="flex items-center gap-[3px]">
        <span class="dot dot-1" />
        <span class="dot dot-2" />
        <span class="dot dot-3" />
      </span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-red-500/70 text-[13px] leading-relaxed pt-1">
      {{ error }}
    </div>

    <!-- Rendered content -->
    <div
      v-else-if="content"
      class="prose prose-sm max-w-none
        prose-headings:font-semibold prose-headings:text-[#1d1d1f] prose-headings:tracking-tight
        prose-p:text-[#1d1d1f]/80 prose-p:leading-[1.7]
        prose-strong:text-[#1d1d1f] prose-strong:font-semibold
        prose-code:text-[12.5px] prose-code:font-medium prose-code:text-[#1d1d1f]/75
        prose-code:bg-black/[0.04] prose-code:px-1.5 prose-code:py-[1px] prose-code:rounded-[5px]
        prose-code:before:content-[''] prose-code:after:content-['']
        prose-pre:bg-[#1d1d1f] prose-pre:text-gray-200 prose-pre:rounded-xl prose-pre:text-[12.5px]
        prose-a:text-blue-500 prose-a:no-underline hover:prose-a:underline
        prose-blockquote:border-blue-500/30 prose-blockquote:text-[#1d1d1f]/60
        prose-li:text-[#1d1d1f]/80"
      v-html="renderedHtml"
    />

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center h-full text-center select-none">
      <p class="text-[13px] text-gray-400/60">选中文本后按快捷键开始翻译</p>
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

<style scoped>
.dot {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.7);
  animation: bounce 1.4s ease-in-out infinite;
}
.dot-2 { animation-delay: 0.16s; }
.dot-3 { animation-delay: 0.32s; }

@keyframes bounce {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  40% {
    transform: translateY(-5px);
    opacity: 1;
  }
}
</style>
