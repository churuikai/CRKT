<template>
  <div class="flex flex-col" :style="{ height: panelHeight + 'px' }">
    <!-- Drag handle -->
    <div
      class="h-[3px] cursor-row-resize bg-transparent hover:bg-blue-400/40 active:bg-blue-500/50 shrink-0 transition-colors"
      @mousedown="startDrag"
    />
    <!-- Header: click to collapse/expand -->
    <button
      class="w-full px-4 py-1.5 text-left text-[12px] text-gray-400 hover:text-gray-600 flex items-center gap-1 shrink-0 transition-colors"
      @click="collapsed = !collapsed"
    >
      <svg
        :class="['w-3 h-3 transition-transform', collapsed ? '' : 'rotate-90']"
        viewBox="0 0 12 12" fill="none"
      >
        <path d="M4 2.5L8 6L4 9.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>原文</span>
      <span v-if="collapsed && text" class="text-gray-300 ml-1 truncate">
        {{ text.slice(0, 60) }}{{ text.length > 60 ? "..." : "" }}
      </span>
    </button>
    <!-- Textarea -->
    <div v-show="!collapsed" class="flex-1 min-h-0 px-4 pb-2">
      <textarea
        v-model="localText"
        class="w-full h-full p-2.5 text-sm text-gray-700 bg-white/60 border border-black/[0.06] rounded-lg resize-none
          focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/30
          placeholder:text-gray-300 transition-shadow"
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
const panelHeight = ref(28);

watch(
  () => props.text,
  (val) => {
    localText.value = val;
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
    panelHeight.value = 28;
  } else if (panelHeight.value < 120) {
    panelHeight.value = 160;
  }
});

function startDrag(e: MouseEvent) {
  const startY = e.clientY;
  const startHeight = panelHeight.value;

  if (collapsed.value) {
    collapsed.value = false;
  }

  function onMove(ev: MouseEvent) {
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
