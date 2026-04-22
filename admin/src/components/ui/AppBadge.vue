<script setup lang="ts">
type Variant = "success" | "warning" | "danger" | "info" | "neutral" | "primary";

withDefaults(
  defineProps<{
    variant?: Variant;
  }>(),
  { variant: "neutral" },
);
</script>

<template>
  <span :class="`badge-${variant}`">
    <slot />
  </span>
</template>
