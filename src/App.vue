<template>
  <div class="flex flex-col h-screen text-gray-800">
    <HistoryToolbar
      :in-history-mode="history.inHistoryMode.value"
      :history-index="history.historyIndex.value"
      :is-translating="translation.isTranslating.value"
      @navigate-up="onNavigateUp"
      @navigate-down="onNavigateDown"
    />
    <TranslationView
      :content="displayContent"
      :is-translating="translation.isTranslating.value"
      :error="translation.error.value"
    />
    <SourceEditor :text="displaySource" @submit="onSourceSubmit" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import HistoryToolbar from "./components/HistoryToolbar.vue";
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
