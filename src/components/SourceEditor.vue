<template>
  <div class="border-t border-gray-200 bg-white">
    <button
      class="w-full px-4 py-2 text-left text-sm text-gray-600 hover:bg-gray-50 flex items-center gap-1"
      @click="expanded = !expanded"
    >
      <span class="text-xs">{{ expanded ? "▼" : "▶" }}</span>
      <span>原文</span>
      <span v-if="text" class="text-gray-400 ml-1 truncate text-xs">
        {{ text.slice(0, 60) }}{{ text.length > 60 ? "..." : "" }}
      </span>
    </button>
    <div v-show="expanded" class="px-4 pb-3">
      <textarea
        ref="textareaRef"
        v-model="localText"
        class="w-full h-28 p-2 text-sm border border-gray-300 rounded resize-y focus:outline-none focus:ring-1 focus:ring-purple-400"
        placeholder="可以手动输入或编辑原文，然后按 Ctrl+Enter 翻译"
        @keydown.ctrl.enter="$emit('submit', localText)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{ text: string }>();
defineEmits<{ submit: [text: string] }>();

const expanded = ref(false);
const localText = ref(props.text);

watch(
  () => props.text,
  (val) => {
    localText.value = val;
  }
);
</script>
