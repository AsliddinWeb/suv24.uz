<script setup lang="ts">
import { Menu, MenuButton, MenuItems } from "@headlessui/vue";
import { EllipsisHorizontalIcon } from "@heroicons/vue/20/solid";
import { computed, ref } from "vue";
import { useElementBounding, useWindowSize } from "@vueuse/core";

const triggerRef = ref<HTMLElement | null>(null);
const { bottom, right } = useElementBounding(triggerRef);
const { width: winW } = useWindowSize();

const MENU_W = 192; // w-48

const position = computed(() => ({
  top: bottom.value + 4,
  left: Math.max(8, Math.min(right.value - MENU_W, winW.value - MENU_W - 8)),
}));
</script>

<template>
  <Menu as="div" class="relative inline-block text-left">
    <MenuButton
      ref="triggerRef"
      class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-500
             hover:bg-slate-100 hover:text-slate-700
             dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
      @click.stop
    >
      <slot name="trigger">
        <EllipsisHorizontalIcon class="h-5 w-5" />
      </slot>
    </MenuButton>
    <Teleport to="body">
      <transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="opacity-0 scale-95 -translate-y-1"
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="opacity-100 scale-100 translate-y-0"
        leave-to-class="opacity-0 scale-95 -translate-y-1"
      >
        <MenuItems
          :style="{ top: position.top + 'px', left: position.left + 'px' }"
          class="fixed z-[70] w-48 origin-top-right rounded-xl bg-white dark:bg-slate-800
                 shadow-lg ring-1 ring-slate-200 dark:ring-slate-700 focus:outline-none py-1"
          @click.stop
        >
          <slot />
        </MenuItems>
      </transition>
    </Teleport>
  </Menu>
</template>
