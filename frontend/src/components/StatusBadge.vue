<template>
  <span class="inline-flex min-w-24 items-center justify-center rounded-full border px-2.5 py-1 text-xs font-semibold" :class="meta.className">
    {{ meta.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue';

import { expirationStatusMeta } from '../utils/ui';

const props = defineProps({
  status: {
    type: String,
    required: true
  }
});

const meta = computed(() => expirationStatusMeta(props.status));
</script>
