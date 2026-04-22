<script setup lang="ts" generic="T extends string | number | boolean | object">
import {
  Listbox,
  ListboxButton,
  ListboxOption,
  ListboxOptions,
} from "@headlessui/vue";
import { ChevronUpDownIcon, CheckIcon } from "@heroicons/vue/20/solid";
import { computed, ref } from "vue";
import { useElementBounding, useWindowSize } from "@vueuse/core";

interface Option {
  value: T;
  label: string;
}

const props = defineProps<{
  modelValue: T | null | undefined;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: T | null): void;
  (e: "change", value: T | null): void;
}>();

const selected = computed(() =>
  props.options.find((o) => o.value === props.modelValue) ?? null,
);

const wrapperRef = ref<HTMLElement | null>(null);
const { bottom: btnBottom, top: btnTop } = useElementBounding(wrapperRef);
const { height: winHeight } = useWindowSize();

const DROPDOWN_MAX_HEIGHT = 260;
const dropUp = computed(() => {
  const spaceBelow = winHeight.value - btnBottom.value;
  const spaceAbove = btnTop.value;
  return spaceBelow < DROPDOWN_MAX_HEIGHT && spaceAbove > spaceBelow;
});

function onChange(value: T | null) {
  emit("update:modelValue", value);
  emit("change", value);
}
</script>

<template>
  <Listbox :model-value="modelValue" :disabled="disabled" @update:model-value="onChange">
    <div ref="wrapperRef" class="relative">
      <ListboxButton
        class="input flex items-center justify-between text-left pr-10 cursor-pointer"
      >
        <span :class="!selected ? 'text-slate-400 dark:text-slate-500' : ''">
          {{ selected ? selected.label : placeholder || "Tanlang..." }}
        </span>
        <ChevronUpDownIcon
          class="pointer-events-none absolute inset-y-0 right-3 my-auto h-5 w-5 text-slate-400"
        />
      </ListboxButton>

      <transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <ListboxOptions
          :class="[
            'absolute z-[60] max-h-60 w-full overflow-auto rounded-lg bg-white dark:bg-slate-800',
            'py-1 text-sm shadow-lg ring-1 ring-slate-200 dark:ring-slate-700 focus:outline-none',
            dropUp ? 'bottom-full mb-1' : 'top-full mt-1',
          ]"
        >
          <ListboxOption
            v-for="opt in options"
            :key="String(opt.value)"
            v-slot="{ active, selected: isSel }"
            :value="opt.value"
            as="template"
          >
            <li
              :class="[
                'relative cursor-pointer select-none px-4 py-2 flex items-center justify-between',
                active
                  ? 'bg-brand-50 text-brand-900 dark:bg-brand-950/60 dark:text-brand-200'
                  : 'text-slate-700 dark:text-slate-200',
              ]"
            >
              <span :class="isSel ? 'font-medium' : ''">{{ opt.label }}</span>
              <CheckIcon v-if="isSel" class="h-4 w-4 text-brand-600 dark:text-brand-400" />
            </li>
          </ListboxOption>
        </ListboxOptions>
      </transition>
    </div>
  </Listbox>
</template>
