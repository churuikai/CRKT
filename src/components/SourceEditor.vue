<template>
  <div class="flex flex-col shrink-0 pb-2" :style="{ height: panelHeight + 'px' }">
    <!-- Drag handle + separator -->
    <div
      class="h-[5px] cursor-row-resize shrink-0 flex items-center justify-center group"
      @mousedown="startDrag"
    >
      <div class="w-8 h-[3px] rounded-full bg-black/[0.06] group-hover:bg-blue-500/30 group-active:bg-blue-500/50 transition-colors" />
    </div>

    <!-- Header: click to collapse/expand -->
    <button
      class="w-full px-4 py-1 text-left text-[11px] text-gray-400/80 hover:text-gray-500 flex items-center gap-1 shrink-0 transition-colors"
      @click="collapsed = !collapsed"
    >
      <svg
        :class="['w-2.5 h-2.5 transition-transform duration-150', collapsed ? '' : 'rotate-90']"
        viewBox="0 0 12 12" fill="none"
      >
        <path d="M4 2.5L8 6L4 9.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="font-medium">原文</span>
      <span v-if="collapsed && text" class="text-gray-400/50 ml-1 truncate max-w-[260px]">
        {{ text.slice(0, 80) }}
      </span>
    </button>

    <!-- Textarea + Send button -->
    <div v-show="!collapsed" class="flex-1 min-h-0 px-4 pb-3">
      <div class="relative w-full h-full">
        <textarea
          v-model="localText"
          class="w-full h-full p-2.5 pr-10 text-[13px] text-[#1d1d1f]/80 leading-relaxed
            bg-white/50 border border-black/[0.05] rounded-lg resize-none
            focus:outline-none focus:ring-2 focus:ring-blue-500/15 focus:border-blue-500/25
            placeholder:text-black/[0.18] transition-shadow"
          placeholder="输入原文，点击发送翻译"
          @keydown.enter.exact="onEnterSubmit"
        />
        <button
          class="absolute right-1.5 bottom-1.5 w-6 h-6 flex items-center justify-center
            rounded-full transition-all duration-200"
          :class="localText.trim()
            ? 'bg-[#1d1d1f]/75 text-white hover:bg-[#1d1d1f]/90 active:scale-90'
            : 'bg-black/[0.03] text-black/[0.10] cursor-default'"
          :disabled="!localText.trim()"
          @click="submit"
        >
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <path d="M8 13V3M3.5 7L8 2.5L12.5 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{ text: string }>();
const emit = defineEmits<{ submit: [text: string] }>();

const collapsed = ref(true);
const localText = ref(props.text);
const panelHeight = ref(24);

function submit() {
  if (localText.value.trim()) {
    emit("submit", localText.value);
  }
}

function onEnterSubmit(e: KeyboardEvent) {
  // Skip when IME is composing (e.g. selecting a Chinese candidate)
  if (e.isComposing) return;
  if (!e.shiftKey && localText.value.trim()) {
    e.preventDefault();
    submit();
  }
}

watch(
  () => props.text,
  (val) => {
    localText.value = val;
    if (val) {
      collapsed.value = false;
      if (panelHeight.value < 120) {
        panelHeight.value = 150;
      }
    }
  }
);

watch(collapsed, (val) => {
  if (val) {
    panelHeight.value = 24;
  } else if (panelHeight.value < 120) {
    panelHeight.value = 150;
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
