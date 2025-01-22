<script setup>

import ProjectCard from "~/components/dashboard/project/project/ProjectCard.vue";
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";
import ConflictCard from "~/components/dashboard/project/conflict/ConflictCard.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";

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

const elem_id = computed(() => {
  return props.collection_data.pk
})

</script>

<template>
  <v-card
    v-for="result in results"
    :key="result[elem_id]"
    class="my-2 d-flex align-center px-3"
    :color="collection_data.color"
    variant="tonal"
  >
    <CardCommon
      :collection_data="collection_data"
      :full_main="result"
      is_select
      @selected-item="selectItem"
    />
<!--    <ProjectCard-->
<!--      v-if="collection_data.snake_name === 'project'"-->
<!--      :full_main="result"-->
<!--    />-->
<!--    <ActorCard-->
<!--      v-else-if="collection_data.snake_name === 'actor'"-->
<!--      :full_main="result"-->
<!--    />-->
<!--    <ConflictCard-->
<!--      v-else-if="collection_data.snake_name === 'conflict'"-->
<!--      :full_main="result"-->
<!--    />-->
<!--    <v-spacer></v-spacer>-->
<!--    <v-btn-->
<!--      color="accent"-->
<!--      variant="text"-->
<!--      icon-->
<!--      class="mr-2"-->
<!--    >-->
<!--      <v-icon>visibility</v-icon>-->
<!--    </v-btn>-->
<!--    <v-btn-->
<!--      @click="selectItem(result)"-->
<!--      color="accent"-->
<!--      variant="outlined"-->
<!--    >-->
<!--      Seleccionar-->
<!--    </v-btn>-->
  </v-card>
</template>

<style scoped>

</style>