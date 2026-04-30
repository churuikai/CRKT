<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">模型</h2>

    <div class="flex items-center gap-2">
      <input
        v-model="newModel"
        class="mac-input flex-1"
        placeholder="输入模型名称"
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
        <input
          v-if="editingIndex === i"
          ref="editInputRef"
          v-model="editingValue"
          class="flex-1 bg-white/80 border border-blue-500/40 rounded px-2 py-0.5 text-[13px] text-[#1d1d1f] outline-none"
          @keydown.enter.prevent="commitEdit(i)"
          @keydown.esc.prevent="cancelEdit"
          @blur="commitEdit(i)"
          @click.prevent.stop
        />
        <span
          v-else
          class="flex-1 text-[13px] text-[#1d1d1f]/80"
          @dblclick.prevent="startEdit(i)"
        >{{ model }}</span>
        <button
          v-if="editingIndex !== i"
          class="text-[11px] text-black/25 hover:text-blue-500 transition-colors"
          @click.prevent="startEdit(i)"
        >
          重命名
        </button>
        <button
          v-if="editingIndex !== i"
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
import { ref, nextTick } from "vue";

const props = defineProps<{ models: string[]; selectedModel: string }>();
const emit = defineEmits<{ update: [models: string[], selected: string] }>();

const newModel = ref("");
const selected = ref(props.selectedModel);
const editingIndex = ref<number | null>(null);
const editingValue = ref("");
const editInputRef = ref<HTMLInputElement | HTMLInputElement[] | null>(null);

function addModel() {
  const name = newModel.value.trim();
  if (!name || props.models.includes(name)) return;
  props.models.push(name);
  newModel.value = "";
  emitUpdate();
}

function removeModel(index: number) {
  const removed = props.models[index];
  props.models.splice(index, 1);
  if (selected.value === removed && props.models.length > 0) {
    selected.value = props.models[0];
  }
  emitUpdate();
}

function startEdit(index: number) {
  editingIndex.value = index;
  editingValue.value = props.models[index];
  nextTick(() => {
    const ref = editInputRef.value;
    const el = Array.isArray(ref) ? ref[0] : ref;
    el?.focus();
    el?.select();
  });
}

function commitEdit(index: number) {
  if (editingIndex.value !== index) return;
  const trimmed = editingValue.value.trim();
  const original = props.models[index];
  editingIndex.value = null;
  if (!trimmed || trimmed === original) return;
  if (props.models.includes(trimmed)) return;
  if (selected.value === original) selected.value = trimmed;
  props.models[index] = trimmed;
  emitUpdate();
}

function cancelEdit() {
  editingIndex.value = null;
}

function emitUpdate() {
  emit("update", [...props.models], selected.value);
}
</script>
