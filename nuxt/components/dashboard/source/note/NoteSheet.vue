<script setup>

import {computed, ref} from 'vue'

import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import FilesToolbar from "~/components/dashboard/utils/FilesToolbar.vue";
const mainStore = useMainStore()
const { saveSimple } = mainStore
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
  collection_data: Object,
})
const dialog_search = ref(false)

const full_note = computed(() => {
  return props.full_main
})

const project_collection = computed(() => {
  return schemas.value.collections_dict['project']
})
const addMention = () => {
  // console.log("add mention 2")
  dialog_search.value = true
}

const SaveMention = (project) => {
  // console.log("save mention", project)
  const params = {
    project: project.id,
    note: props.full_main.id,
  }
  saveSimple(['mention', params]).then(response => {
    // console.log("response", response)
    full_note.value.mentions.unshift(response)
    dialog_search.value = false
  })
}

function closeDialog(event) {
  // dialog_search.value = false
  // console.log("close dialog", event)
  if (event) {
    // project_in_edition.value = event
    SaveMention(event)
  }
  else {
    dialog_search.value = false
  }
}

function saveMention(mention) {
  const index = full_note.value.mentions.findIndex(
    item => item.id === mention.id)
  full_note.value.mentions.splice(index, 1, mention)
}

</script>

<template>
  <v-card
    v-if="full_note"
    class="mb-4"
    elevation="4"
    variant="elevated"
    color="brown-lighten-4"
  >
    <FilesToolbar
      :full_main="full_main"
      child_relation_name="note_file"
      main_collection_name="note"
    />
  </v-card>
  <v-card v-if="full_note.mentions" elevation="5">
    <v-card-title>
      <div class="d-flex">
        {{ full_note.mentions.length }} menciones de proyectos
        <v-spacer></v-spacer>
        <v-btn
          @click="addMention"
          color="accent"
          variant="outlined"
          prepend-icon="add"
          text="Agregar mención"
        ></v-btn>
      </div>
    </v-card-title>
    <v-card-text>
      <v-row>
        <MentionDetails
          v-for="mention in full_note.mentions"
          :key="mention.id"
          :mention="mention"
          is_full
          @mention-saved="saveMention"
        />
      </v-row>
    </v-card-text>
    <v-card-actions v-if="full_note.mentions.length">
      <v-spacer></v-spacer>
      <v-btn
        @click="addMention"
        color="accent"
        variant="outlined"
        prepend-icon="add"
        text="Agregar mención"
      ></v-btn>
    </v-card-actions>
    <v-dialog
      v-model="dialog_search"
      max-width="920"
    >
      <v-card height="800">
        <v-card-text class="py-0">
          <CollectionDisplay
            :parent_collection="project_collection"
            is_mini
            @select-item="closeDialog($event)"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
<!--  <v-card class="my-3" elevation="3">-->
<!--    <v-card-title>-->
<!--      -&#45;&#45;&#45;&#45;-->
<!--    </v-card-title>-->
<!--    <v-card-text v-if="!full_note.mentions">-->
<!--      {{full_note}}-->
<!--    </v-card-text>-->
<!--  </v-card>-->
</template>

<style scoped>

</style>