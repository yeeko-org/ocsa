<script setup>
const props = defineProps({
  description: {
    type: String,
    required: false,
  },
})

</script>

<template>
  <v-btn
    v-if="description"
    icon
    variant="text"
  >
    <v-icon
      color="grey-darken-1"
    >
      subject
    </v-icon>
    <v-tooltip
      activator="parent"
      location="end"
      max-width="400"
    >
      {{ description }}
    </v-tooltip>
  </v-btn>
</template>

<style scoped>

</style>