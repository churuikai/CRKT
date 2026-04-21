import { ref, onMounted, onUnmounted } from "vue";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/core";

interface TranslationRecord {
  id: string;
  source_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
  timestamp: string;
  model: string;
  skill: string;
}

export function useHistory() {
  const inHistoryMode = ref(false);
  const historyIndex = ref(-1);
  const historyRecord = ref<TranslationRecord | null>(null);

  const unlisteners: UnlistenFn[] = [];

  onMounted(async () => {
    unlisteners.push(
      await listen("history:exited", () => {
        inHistoryMode.value = false;
        historyIndex.value = -1;
        historyRecord.value = null;
      })
    );
  });

  onUnmounted(() => {
    unlisteners.forEach((fn) => fn());
  });

  async function navigateUp() {
    const record = await invoke<TranslationRecord | null>(
      "history_navigate_up"
    );
    if (record) {
      inHistoryMode.value = true;
      historyRecord.value = record;
      historyIndex.value = await invoke<number>("history_get_pointer");
    }
  }

  async function navigateDown() {
    const record = await invoke<TranslationRecord | null>(
      "history_navigate_down"
    );
    if (record) {
      historyRecord.value = record;
      historyIndex.value = await invoke<number>("history_get_pointer");
    } else {
      inHistoryMode.value = false;
      historyIndex.value = -1;
      historyRecord.value = null;
    }
  }

  async function exitHistoryMode() {
    await invoke("history_exit");
    inHistoryMode.value = false;
    historyIndex.value = -1;
    historyRecord.value = null;
  }

  return {
    inHistoryMode,
    historyIndex,
    historyRecord,
    navigateUp,
    navigateDown,
    exitHistoryMode,
  };
}
