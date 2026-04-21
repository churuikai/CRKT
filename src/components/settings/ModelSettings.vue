<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">模型</h2>

    <div class="flex items-center gap-2">
      <input
        v-model="newModel"
        class="mac-input flex-1"
        placeholder="输入模型名称"
        @keydown.enter="addModel"
      />
      <button
        class="px-3 py-[7px] text-[13px] text-blue-500 font-medium rounded-lg hover:bg-blue-500/[0.07] active:bg-blue-500/[0.12] transition-colors"
        @click="addModel"
      >
        + 添加
      </button>
    </div>

    <div class="mac-card overflow-hidden divide-y divide-black/[0.04]">
      <label
        v-for="(model, i) in models"
        :key="i"
        class="flex items-center gap-3 px-4 py-[10px] cursor-pointer transition-colors"
        :class="model === selected ? 'bg-blue-500/[0.04]' : 'hover:bg-black/[0.02]'"
      >
        <input
          type="radio"
          :value="model"
          v-model="selected"
          class="accent-blue-500"
          @change="emitUpdate"
        />
        <span class="flex-1 text-[13px] text-[#1d1d1f]/80">{{ model }}</span>
        <button
          class="text-[11px] text-black/20 hover:text-red-500 transition-colors"
          @click.prevent="removeModel(i)"
        >
          移除
        </button>
      </label>
      <div v-if="models.length === 0" class="px-4 py-8 text-center text-[13px] text-black/25">
        暂无模型
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ models: string[]; selectedModel: string }>();
const emit = defineEmits<{ update: [models: string[], selected: string] }>();

const newModel = ref("");
const selected = ref(props.selectedModel);

function addModel() {
  if (newModel.value.trim() && !props.models.includes(newModel.value.trim())) {
    props.models.push(newModel.value.trim());
    newModel.value = "";
    emitUpdate();
  }
}

function removeModel(index: number) {
  const removed = props.models[index];
  props.models.splice(index, 1);
  if (selected.value === removed && props.models.length > 0) {
    selected.value = props.models[0];
  }
  emitUpdate();
}

function emitUpdate() {
  emit("update", [...props.models], selected.value);
}
</script>
