<template>
  <div class="flex flex-col h-screen">
    <!-- Draggable title bar region -->
    <div class="h-7 shrink-0 flex items-end px-3 pb-0.5 select-none">
      <div class="flex items-center gap-1">
        <button
          class="w-5 h-5 flex items-center justify-center text-gray-400 rounded hover:bg-black/[0.05] active:bg-black/[0.08] transition-colors"
          title="上翻历史"
          @click="onNavigateUp"
        >
          <svg width="10" height="10" viewBox="0 0 12 12" fill="none"><path d="M2.5 7.5L6 4L9.5 7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <button
          class="w-5 h-5 flex items-center justify-center text-gray-400 rounded hover:bg-black/[0.05] active:bg-black/[0.08] transition-colors"
          title="下翻历史"
          @click="onNavigateDown"
        >
          <svg width="10" height="10" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <span
          v-if="history.inHistoryMode.value"
          class="text-[10px] text-gray-400/70 tabular-nums ml-0.5"
        >
          #{{ history.historyIndex.value + 1 }}
        </span>
      </div>
    </div>

    <!-- Translation content -->
    <TranslationView
      :content="displayContent"
      :is-translating="translation.isTranslating.value"
      :error="translation.error.value"
      class="flex-1 min-h-0"
    />

    <!-- Source editor -->
    <SourceEditor :text="displaySource" @submit="onSourceSubmit" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import TranslationView from "./components/TranslationView.vue";
import SourceEditor from "./components/SourceEditor.vue";
import { useTranslation } from "./composables/useTranslation";
import { useHistory } from "./composables/useHistory";

const translation = useTranslation();
const history = useHistory();

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
</script>
