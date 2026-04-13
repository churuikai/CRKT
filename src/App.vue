<template>
  <div class="flex flex-col h-screen bg-gray-50 text-gray-900">
    <HistoryToolbar
      :in-history-mode="history.inHistoryMode.value"
      :history-index="history.historyIndex.value"
      :is-translating="translation.isTranslating.value"
      @navigate-up="onNavigateUp"
      @navigate-down="onNavigateDown"
    />

    <!-- Comparison mode: side by side -->
    <div v-if="comparisonMode" class="flex flex-1 overflow-hidden">
      <div class="flex-1 overflow-auto p-4 border-r border-gray-200">
        <div class="text-xs text-gray-400 mb-2">原文</div>
        <pre class="whitespace-pre-wrap text-sm">{{ displaySource }}</pre>
      </div>
      <div
        class="w-1 cursor-col-resize bg-gray-200 hover:bg-purple-400 active:bg-purple-500"
        @mousedown="startDrag"
      />
      <TranslationView
        class="flex-1"
        :content="displayContent"
        :is-translating="translation.isTranslating.value"
        :error="translation.error.value"
      />
    </div>

    <!-- Single column mode (default) -->
    <template v-else>
      <TranslationView
        :content="displayContent"
        :is-translating="translation.isTranslating.value"
        :error="translation.error.value"
      />
      <SourceEditor :text="displaySource" @submit="onSourceSubmit" />
    </template>

    <StatusBar />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import HistoryToolbar from "./components/HistoryToolbar.vue";
import TranslationView from "./components/TranslationView.vue";
import SourceEditor from "./components/SourceEditor.vue";
import StatusBar from "./components/StatusBar.vue";
import { useTranslation } from "./composables/useTranslation";
import { useHistory } from "./composables/useHistory";

const translation = useTranslation();
const history = useHistory();
const comparisonMode = ref(false);

const unlisteners: UnlistenFn[] = [];

onMounted(async () => {
  unlisteners.push(
    await listen<boolean>("config:comparison_changed", (e) => {
      comparisonMode.value = e.payload;
    })
  );
});

onUnmounted(() => unlisteners.forEach((fn) => fn()));

const displayContent = computed(() => {
  if (history.inHistoryMode.value && history.historyRecord.value) {
    return history.historyRecord.value.translated_text;
  }
  return translation.translationContent.value;
});

const displaySource = computed(() => {
  if (history.inHistoryMode.value && history.historyRecord.value) {
    return history.historyRecord.value.source_text;
  }
  return translation.sourceText.value;
});

function onNavigateUp() {
  history.navigateUp();
}
function onNavigateDown() {
  history.navigateDown();
}

function onSourceSubmit(text: string) {
  if (history.inHistoryMode.value) {
    history.exitHistoryMode();
  }
  translation.translate(text);
}

// Simple drag-to-resize for comparison mode divider
function startDrag(e: MouseEvent) {
  const startX = e.clientX;
  const container = (e.target as HTMLElement).parentElement!;
  const left = container.children[0] as HTMLElement;
  const startWidth = left.offsetWidth;

  function onMove(ev: MouseEvent) {
    const delta = ev.clientX - startX;
    left.style.flex = "none";
    left.style.width = `${startWidth + delta}px`;
  }
  function onUp() {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  }
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}
</script>
