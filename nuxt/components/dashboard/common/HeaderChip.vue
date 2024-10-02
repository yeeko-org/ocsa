<script setup>

import { computed } from 'vue'

const props = defineProps({
  count: Number,
  icon: String,
  label: {
    type: String,
    default: 'elemento'
  },
  // label_plural: {
  //   type: String,
  //   default: 'elementos'
  // },
  label_plural: {
    type: String,
    default: 'elementos'
  },
  color: String,
  tooltip_complement: String,
})

const final_label = computed(() => {
  return props.count === 1 ? props.label : props.label_plural
})

</script>

<template>
  <v-chip
    small
    label
    variant="tonal"
    :color="color"
  >
    <v-icon
      v-if="!count"
      small
      color="warning"
    >
      warning_amber
    </v-icon>
    <span v-else>
      {{count}}
    </span>
    <v-icon
      small
      end
      :color="color"
    >
      {{ icon }}
    </v-icon>
    <v-tooltip
      activator="parent"
      location="top"
      :bg-color="color"
      :color="color"
      _style="`background-color: ${color};`"
    >
      <div class="font-weight-bold">
        {{count}} {{ final_label }}
      </div>
      <!--style with break-word-->
      <div
        v-if="tooltip_complement"
        v-html="tooltip_complement"
        style="max-width: 400px; word-wrap: break-word;"
      ></div>

    </v-tooltip>
  </v-chip>

</template>

<style scoped>

</style>