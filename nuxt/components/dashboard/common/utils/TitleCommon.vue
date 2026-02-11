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
})

</script>

<template>
  <v-card
    :class="card_class"
    variant="flat"
    color="transparent"
    style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
    :style="`width: ${title_width}px;`"
  >
    {{ title_text }}
    <v-tooltip
      activator="parent"
      location="bottom"
      :max-width="400"
    >
      {{ title_text }}
    </v-tooltip>
  </v-card>
</template>

<style scoped>

</style>