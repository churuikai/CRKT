import { ref, onMounted, onUnmounted } from "vue";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/core";

export function useTranslation() {
  const translationContent = ref("");
  const sourceText = ref("");
  const isTranslating = ref(false);
  const error = ref("");

  const unlisteners: UnlistenFn[] = [];

  onMounted(async () => {
    unlisteners.push(
      await listen<string>("translation:chunk", (e) => {
        translationContent.value = e.payload;
        isTranslating.value = true;
        error.value = "";
      })
    );
    unlisteners.push(
      await listen<string>("translation:complete", (e) => {
        translationContent.value = e.payload;
        isTranslating.value = false;
      })
    );
    unlisteners.push(
      await listen<string>("translation:error", (e) => {
        error.value = e.payload;
        isTranslating.value = false;
      })
    );
    unlisteners.push(
      await listen<string>("source:update", (e) => {
        sourceText.value = e.payload;
      })
    );
    unlisteners.push(
      await listen<string>("source:append", (e) => {
        sourceText.value += e.payload;
      })
    );
    unlisteners.push(
      await listen("translation:started", () => {
        isTranslating.value = true;
        error.value = "";
        translationContent.value = "";
      })
    );
  });

  onUnmounted(() => {
    unlisteners.forEach((fn) => fn());
  });

  async function translate(text: string) {
    await invoke("translate", { text });
  }

  async function cancel() {
    await invoke("cancel_translation");
  }

  return {
    translationContent,
    sourceText,
    isTranslating,
    error,
    translate,
    cancel,
  };
}
