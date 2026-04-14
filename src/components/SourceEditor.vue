<template>
  <div class="flex flex-col bg-white" :style="{ height: panelHeight + 'px' }">
    <!-- Drag handle -->
    <div
      class="h-1 cursor-row-resize bg-gray-200 hover:bg-purple-400 active:bg-purple-500 shrink-0"
      @mousedown="startDrag"
    />
    <!-- Header: click to collapse/expand -->
    <button
      class="w-full px-4 py-1.5 text-left text-sm text-gray-600 hover:bg-gray-50 flex items-center gap-1 shrink-0"
      @click="collapsed = !collapsed"
    >
      <span class="text-xs">{{ collapsed ? "▶" : "▼" }}</span>
      <span>原文</span>
      <span v-if="collapsed && text" class="text-gray-400 ml-1 truncate text-xs">
        {{ text.slice(0, 60) }}{{ text.length > 60 ? "..." : "" }}
      </span>
    </button>
    <!-- Textarea -->
    <div v-show="!collapsed" class="flex-1 min-h-0 px-4 pb-2">
      <textarea
        v-model="localText"
        class="w-full h-full p-2 text-sm border border-gray-300 rounded resize-none focus:outline-none focus:ring-1 focus:ring-purple-400"
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

const collapsed = ref(true);
const localText = ref(props.text);
const panelHeight = ref(32); // collapsed: just the header

watch(
  () => props.text,
  (val) => {
    localText.value = val;
    // Auto-expand when source text arrives
    if (val) {
      collapsed.value = false;
      if (panelHeight.value < 120) {
        panelHeight.value = 160;
      }
    }
  }
);

watch(collapsed, (val) => {
  if (val) {
    panelHeight.value = 32;
  } else if (panelHeight.value < 120) {
    panelHeight.value = 160;
  }
});

function startDrag(e: MouseEvent) {
  const startY = e.clientY;
  const startHeight = panelHeight.value;

  // Expand if collapsed when dragging
  if (collapsed.value) {
    collapsed.value = false;
  }

  function onMove(ev: MouseEvent) {
    // Dragging up = larger panel
    const delta = startY - ev.clientY;
    panelHeight.value = Math.max(60, Math.min(window.innerHeight * 0.7, startHeight + delta));
  }
  function onUp() {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  }
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}
</script>
