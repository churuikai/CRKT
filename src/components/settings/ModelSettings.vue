<template>
  <div class="space-y-4">
    <div class="flex gap-2">
      <input
        v-model="newModel"
        class="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
        placeholder="输入模型名称"
        @keydown.enter="addModel"
      />
      <button
        class="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
        @click="addModel"
      >
        添加
      </button>
    </div>
    <div class="space-y-1">
      <div
        v-for="(model, i) in models"
        :key="i"
        class="flex items-center gap-2 px-2 py-1 rounded"
        :class="model === selectedModel ? 'bg-purple-50' : 'hover:bg-gray-50'"
      >
        <input
          type="radio"
          :value="model"
          v-model="selected"
          @change="emitUpdate"
        />
        <span class="flex-1 text-sm">{{ model }}</span>
        <button
          class="text-red-400 hover:text-red-600 text-xs"
          @click="removeModel(i)"
        >
          删除
        </button>
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
