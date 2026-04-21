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

    <div class="mac-card px-5 py-4">
      <p class="text-[13px] text-[#1d1d1f]/40">Translator v0.1.0</p>
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
import { ref } from "vue";

const props = defineProps<{ startOnBoot: boolean }>();
defineEmits<{ update: [partial: Record<string, boolean>] }>();

const autostart = ref(props.startOnBoot);
</script>
