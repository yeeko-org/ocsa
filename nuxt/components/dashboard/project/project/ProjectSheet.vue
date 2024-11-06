<script setup>

import NoteHeader from "~/components/dashboard/source/note/NoteHeader.vue";
import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";

import { ref, computed } from 'vue'
import ProjectEdit from "~/components/dashboard/project/project/ProjectEdit.vue";
import {useMainStore} from "~/store/index";
import {storeToRefs} from "pinia";
import PanelList from "~/components/dashboard/common/PanelList.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
})

const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})

const openNote = () => {
  console.log("open note")
}

const full_project = computed(() => {
  return props.full_main
})

const related_notes = computed(() => {
  return full_project.value.mentions.map(mention => {
    const full_mention = {...mention, project: full_project.value}
    return {
      ...mention.note,
      mentions: [full_mention]
    }
  })

})

</script>

<template>
  <v-card v-if="full_project.mentions">
    <v-card-title class="text-deep-purple">
      {{ full_project.mentions.length }} Notas:
    </v-card-title>
    <v-card-text>
      <PanelList
        v-if="true"
        :results="related_notes"
        :collection_data="note_collection"
        :show_details="show_details"
      />
    </v-card-text>

  </v-card>
  <v-card class="my-3">
    <v-card-title>
      Todos los actores:
    </v-card-title>
  </v-card>
</template>

<style scoped>

</style>