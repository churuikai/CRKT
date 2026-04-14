<template>
  <div class="space-y-4">
    <label class="flex items-center gap-2 cursor-pointer">
      <input
        type="checkbox"
        v-model="autostart"
        class="rounded"
        @change="$emit('update', { startOnBoot: autostart })"
      />
      <span class="text-sm">开机自启动</span>
    </label>
    <div class="pt-4 border-t border-gray-200 text-sm text-gray-500">
      <p>CRKT Translator v0.1.0</p>
      <p class="mt-1">
        <a
          href="https://github.com/churuikai/CRKT"
          class="text-blue-500 hover:underline"
          >GitHub</a
        >
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
