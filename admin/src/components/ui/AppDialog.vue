<script setup lang="ts">
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from "@headlessui/vue";
import { XMarkIcon } from "@heroicons/vue/24/outline";

const props = withDefaults(
  defineProps<{
    open: boolean;
    title?: string;
    maxWidth?: string;
  }>(),
  { maxWidth: "max-w-lg" },
);

const emit = defineEmits<{ (e: "update:open", value: boolean): void }>();

function close() {
  emit("update:open", false);
}
</script>

<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-50" @close="close">
      <TransitionChild
        as="template"
        enter="ease-out duration-200"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="ease-out duration-200"
            enter-from="opacity-0 translate-y-4 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-150"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:scale-95"
          >
            <DialogPanel
              :class="[
                'card relative w-full transform transition-all',
                maxWidth,
              ]"
            >
              <div class="flex items-start justify-between gap-4 px-6 pt-5 pb-3">
                <DialogTitle
                  v-if="title"
                  class="text-base font-semibold text-slate-900 dark:text-slate-100"
                >
                  {{ title }}
                </DialogTitle>
                <slot name="title" />
                <button
                  type="button"
                  class="btn-ghost -mr-2 -mt-1 !p-1.5"
                  @click="close"
                  aria-label="Close"
                >
                  <XMarkIcon class="h-5 w-5" />
                </button>
              </div>
              <div class="px-6 pb-4">
                <slot />
              </div>
              <div
                v-if="$slots.footer"
                class="flex items-center justify-end gap-2 px-6 py-4 border-t border-slate-200 dark:border-slate-800"
              >
                <slot name="footer" />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
