<script setup>
const props = defineProps({
  main: Object,
})
</script>

<template>
  <div>
  <v-icon class="ml-2 align-self-center" color="yellow-accent-4">
    sticky_note_2
  </v-icon>
    <v-tooltip
      activator="parent"
      top
      content-class="pa-0"
    >
      <v-card
        color="yellow-accent-4"
        class="pa-2 ma-0"
        width="560"
        style="white-space: pre-line;"
        v-html="main.comments"
      >
      </v-card>
    </v-tooltip>
  </div>
</template>

<style scoped>

</style>