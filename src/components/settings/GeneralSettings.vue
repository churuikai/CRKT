<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">通用</h2>

    <div class="mac-card divide-y divide-black/[0.04]">
      <div class="flex items-center justify-between px-5 py-3.5">
        <span class="text-[13px] text-[#1d1d1f]/80">开机自启动</span>
        <button
          type="button"
          role="switch"
          :aria-checked="autostart"
          class="relative inline-flex h-[22px] w-[40px] shrink-0 rounded-full transition-colors duration-200 ease-in-out
            focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/30"
          :class="autostart ? 'bg-blue-500' : 'bg-black/[0.09]'"
          @click="autostart = !autostart; $emit('update', { startOnBoot: autostart })"
        >
          <span
            class="pointer-events-none inline-block h-[18px] w-[18px] rounded-full bg-white shadow-sm transition-transform duration-200 ease-in-out"
            :class="autostart ? 'translate-x-[20px]' : 'translate-x-[2px]'"
            style="margin-top: 2px"
          />
        </button>
      </div>
    </div>

    <div class="mac-card divide-y divide-black/[0.04]">
      <div class="flex items-center justify-between px-5 py-3.5">
        <div>
          <div class="text-[13px] text-[#1d1d1f]/80">翻译缓存</div>
          <div class="text-[11px] text-black/40 mt-0.5">
            {{ cacheSize === null ? "加载中…" : `${cacheSize} 条` }}
          </div>
        </div>
        <button
          class="px-3 py-[5px] text-[12px] text-red-500/70 font-medium rounded-lg hover:bg-red-500/[0.07] active:bg-red-500/[0.12] transition-colors disabled:opacity-25 disabled:pointer-events-none"
          :disabled="!cacheSize"
          @click="onClearCache"
        >
          清除
        </button>
      </div>
      <div class="flex items-center justify-between px-5 py-3.5">
        <div>
          <div class="text-[13px] text-[#1d1d1f]/80">翻译历史</div>
          <div class="text-[11px] text-black/40 mt-0.5">用于历史记录上下导航</div>
        </div>
        <button
          class="px-3 py-[5px] text-[12px] text-red-500/70 font-medium rounded-lg hover:bg-red-500/[0.07] active:bg-red-500/[0.12] transition-colors"
          @click="onClearHistory"
        >
          清除
        </button>
      </div>
    </div>

    <div class="mac-card px-5 py-4">
      <p class="text-[13px] text-[#1d1d1f]/40">Translator v{{ version || "—" }}</p>
      <p class="mt-1.5">
        <a
          href="https://github.com/churuikai/CRKT"
          class="text-[13px] text-blue-500 hover:text-blue-600 transition-colors"
        >GitHub</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { getVersion } from "@tauri-apps/api/app";

const props = defineProps<{ startOnBoot: boolean }>();
defineEmits<{ update: [partial: Record<string, boolean>] }>();

const autostart = ref(props.startOnBoot);
const version = ref("");
const cacheSize = ref<number | null>(null);

async function loadCacheStats() {
  try {
    const stats = await invoke<{ size: number }>("get_cache_stats");
    cacheSize.value = stats.size;
  } catch {
    cacheSize.value = 0;
  }
}

async function onClearCache() {
  if (!confirm(`确认清除翻译缓存（${cacheSize.value} 条）？`)) return;
  await invoke("clear_cache");
  await loadCacheStats();
}

async function onClearHistory() {
  if (!confirm("确认清除全部翻译历史记录？")) return;
  await invoke("history_clear");
}

onMounted(async () => {
  try {
    version.value = await getVersion();
  } catch {
    /* ignore — keeps the dash */
  }
  await loadCacheStats();
});
</script>
