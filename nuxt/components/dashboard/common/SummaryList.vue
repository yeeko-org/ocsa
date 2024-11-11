<script setup>

import ProjectCard from "~/components/dashboard/project/project/ProjectCard.vue";
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";

const props = defineProps({
  results: Array,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const emits = defineEmits(['select-item'])

function selectItem(result) {
  console.log("item selected", result)
  emits('select-item', result)
}

</script>

<template>
  <v-card
    v-for="result in results"
    :key="result.id"
    class="my-2 d-flex align-center px-3"
    :color="collection_data.color"
    variant="tonal"
  >
    <ProjectCard
      v-if="collection_data.snake_name === 'project'"
      :full_main="result"
    />
    <ActorCard
      v-else-if="collection_data.snake_name === 'actor'"
      :full_main="result"
    />
    <v-spacer></v-spacer>
    <v-btn
      @click="selectItem(result)"
      color="accent"
      variant="outlined"
    >
      Seleccionar
    </v-btn>
  </v-card>
</template>

<style scoped>

</style>