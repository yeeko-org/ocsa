<script setup>
const props = defineProps({
  help_text: {
    type: String,
    required: false,
  }
})
</script>

<template>
  <v-alert
    v-if="help_text"
    type="info"
    variant="tonal"
    border="end"
    closable
    density="compact"
  >
    <template #text>
      <div
        v-html="help_text"
        style="white-space: pre-wrap;"
      >
      </div>
    </template>
  </v-alert>

</template>

<style scoped>

</style>