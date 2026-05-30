<script setup>

const props = defineProps({
  title_text: {
    type: String,
    required: true,
  },
  title_width: {
    type: Number,
    default: 300,
  },
  card_class: {
    type: String,
    default: 'ml-2 font-weight-bold',
  },
  max_height: {
    type: Number,
    default: 54,
  },
})

</script>

<template>
  <div
    :class="card_class"
    style="text-wrap: pretty; overflow: hidden;"
    :style="`width: ${title_width}px; max-height: ${max_height}px;`"
  >
    {{ title_text }}
    <v-tooltip
      activator="parent"
      location="bottom"
      :max-width="400"
    >
      {{ title_text }}
    </v-tooltip>
  </div>
</template>

<style scoped>

</style>