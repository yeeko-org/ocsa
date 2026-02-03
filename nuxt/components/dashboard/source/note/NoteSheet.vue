<script setup>

import {computed, ref} from 'vue'

import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import FilesToolbar from "~/components/dashboard/utils/FilesToolbar.vue";
import ParagraphsContent from "~/components/dashboard/source/ParagraphsContent.vue";
const mainStore = useMainStore()
const { saveSimple, getSimple, savePreCapture } = mainStore
const { schemas } = storeToRefs(mainStore)
import { useSaveElements } from "~/composables/save_elements.js";
import { mixOrigins, orderMix} from "~/composables/pre_capture.js";
import ParagraphsProjectsContent from "~/components/dashboard/source/ParagraphsProjectsContent.vue";
const { saveComplex } = useSaveElements()

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

const mentionDetailsRef = ref([])
const all_mentions = ref([])

const project_collection = computed(() => {
  return schemas.value.collections_dict['project']
})

const snackbar_message = ref('')
const snackbar = ref(false)

const dialog_search = ref(false)
const addMention = () => {
  // console.log("add mention 2")
  dialog_search.value = true
}

onMounted(() => {
  const mixed_mentions = orderMix(
    'mentions',
    props.full_main.mentions || [],
    props.full_main.pre_mentions || [])
  console.log("mixed_mentions", mixed_mentions)
  all_mentions.value = mixed_mentions
})

const mention_created = ref(null)

const addNewMention = (project) => {
  // console.log("save mention", project)
  const params = {
    project: project.id,
    note: props.full_main.id,
  }
  const mentions_count = all_mentions.value.length
  saveSimple(['mention', params]).then(response => {
    mention_created.value = response.id
    all_mentions.value.unshift(response)
    dialog_search.value = false
    if (mentions_count > 0) {
      dialog_copy.value = true
    }
  })
}

function closeDialog(event) {
  if (event) {
    addNewMention(event)
  }
  else {
    dialog_search.value = false
  }
}

const dialog_copy = ref(false)

function discardPreMention(pre_item) {
  const data = {
    path: pre_item.path,
    discarded: true,
  }
  savePreCapture({data, note_id: props.full_main.id}).then((res) => {
    snackbar.value = true
    snackbar_message.value = 'Se ha descartado la mención preliminar'
    console.log("res", res)
    // allCopyFinished()
  })
}

function changePreMention(pre_item, project) {
  const params = {
    project: project.id,
    note: props.full_main.id,
  }
  saveSimple(['mention', params]).then(saved_item => {
    const path = pre_item.path
    const index = all_mentions.value.findIndex(item => (item.path === path))
    const data = {
      path,
      element_id: saved_item.id,
      discarded: false,
    }
    savePreCapture({data, note_id: props.full_main.id}).then((res) => {
      snackbar.value = true
      snackbar_message.value = 'Se ha aceptado la mención preliminar'
      // console.log("res", res)
      // allCopyFinished(saved_item.id)
      const mixed_item = mixOrigins(saved_item, res.content, 1)
      all_mentions.value.splice(index, 1, mixed_item)
    })
  })
}

function saveMention(mention) {
  const index = all_mentions.value.findIndex(
    item => item.id === mention.id)
  all_mentions.value.splice(index, 1, mention)
  snackbar.value = true
  snackbar_message.value = 'Se ha guardado la mención'

}

function deleteMention(mention_id) {
  const index = all_mentions.value.findIndex(
    item => item.id === mention_id)
  if (index > -1) {
    all_mentions.value.splice(index, 1)
  }
  snackbar.value = true
  snackbar_message.value = 'Se ha eliminado la mención'
}

function allCopyFinished(mention_id=null) {
  mentionDetailsRef.value.forEach(mentionComp => {
    mentionComp.allFinished(mention_id)
  })
}

function copyMention(mention_to_copy) {

  // console.log("mention_to_copy", mention_to_copy)
  const new_mention = {...mention_to_copy}
  saveComplex('mention', new_mention, mention_created.value)
    .then(() => {
      dialog_copy.value = false
      allCopyFinished(mention_created.value)
    })
}

const two_columns = ref(false)

</script>

<template>

  <v-switch
    v-model="two_columns"
    color="accent"
    hide-details
    density="compact"
    label="Dos columnas"
  ></v-switch>

  <v-row :class="{ 'dual-scroll-layout': two_columns }">

    <v-col
      :cols="two_columns ? 4 : 12"
      :class="[two_columns ? 'pa-0' : '', { 'scroll-column': two_columns }]"
    >
      <v-card
        v-if="full_main"
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
        <ParagraphsProjectsContent
          v-if="full_main.articles.length > 0 && full_main.articles[0].second_criteria"
          :full_main="full_main.articles[0]"
          :sending_link="false"
          :note_id="full_main.id"
          class="ma-2 px-2"
          :show_init="false"
        />

        <ParagraphsContent
          v-else-if="full_main.articles.length > 0"
          :full_main="full_main.articles[0]"
          :sending_link="false"
          class="ma-2 px-2"
          :show_init="false"
        ></ParagraphsContent>
      </v-card>
    </v-col>
    <v-col
      :cols="two_columns ? 8 : 12"
      :class="[two_columns ? 'pa-0' : '', { 'scroll-column': two_columns }]"
    >
      <v-card v-if="all_mentions" elevation="5">
        <v-card-title>
          <div class="d-flex">
            {{ all_mentions.length }} menciones de proyectos
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
              v-for="mention in all_mentions"
              :key="mention.id"
              :mention="mention"
              :note_id="full_main.id"
              ref="mentionDetailsRef"
              is_full
              @mention-saved="saveMention"
              @mention-deleted="deleteMention"
              @mention-accepted="changePreMention(mention, $event)"
              @mention-discarded="discardPreMention(mention)"
            />
          </v-row>
        </v-card-text>
        <v-card-actions v-if="all_mentions.length">
          <v-spacer></v-spacer>
          <v-btn
            @click="addMention"
            color="accent"
            variant="outlined"
            prepend-icon="add"
            text="Agregar mención"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
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
    <v-dialog
      v-model="dialog_copy"
      max-width="600"
    >
      <v-card height="800">
        <v-card-title class="text-no-wrap no-wrap">
          ¿Te gustaría copiar la información de la primer mención?
        </v-card-title>
        <v-card-text>
          <template
            v-for="mention in all_mentions"
            :key="mention.id"
          >
            <v-card
              v-if="mention.id !== mention_created"
              class="my-2 pa-3 d-flex align-center"
              variant="tonal"
              color="purple"
            >
              <div class="text-h6">

                {{mention.project_full.name}}
              </div>
              <v-spacer></v-spacer>
              <v-btn
                class="ml-3"
                color="accent "
                variant="outlined"
                @click="copyMention(mention)"
              >
                Seleccionar
              </v-btn>
            </v-card>

          </template>

        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="accent"
            @click="dialog_copy = false"
            variant="text"
          >
            No copiar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar"
      color="success"
      location="right bottom"
      location-strategy="connected"
      timeout="3500"
    >
      {{ snackbar_message || 'Cambios guardados' }}
      <template v-slot:actions>
        <v-btn
          color="accent"
          variant="text"
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-row>
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

.dual-scroll-layout {
  height: calc(100vh - 100px); /* Ajusta según tu layout */
  flex-wrap: nowrap !important;
  margin-top: 8px;
}

.scroll-column {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Scrollbar personalizado (opcional) */
.scroll-column::-webkit-scrollbar {
  width: 8px;
}

.scroll-column::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.scroll-column::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.scroll-column::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>