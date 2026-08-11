<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {useDashboardStore} from "~/store/dash.js";
const mainStore = useMainStore()
const dashboardStore = useDashboardStore()

import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import FilesToolbar from "~/components/dashboard/capture/FilesToolbar.vue";
import ParagraphsContent from "~/components/dashboard/capture/ParagraphsContent.vue";
import ParagraphsProjectsContent from "~/components/dashboard/capture/ParagraphsProjectsContent.vue";

const { saveSimple, sendPreCapture } = mainStore
const { schemas } = storeToRefs(mainStore)
const { showSnackbar } = dashboardStore
import { useSaveElements } from "~/composables/save_elements.js";
import {discardPreItem, orderMix, savePreItem} from "~/composables/mix_pre_capture.js";
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
// const full_main = defineModel({type: Object, required: true})

const mentionDetailsRef = ref([])
const all_mentions = ref([])
const note_files = ref([])

const project_collection = computed(() => {
  return schemas.value.collections_dict['project']
})

const dialog_search = ref(false)
const addMention = () => {
  // console.log("add mention 2")
  dialog_search.value = true
}
const loading_precapture = ref(false)

async function preCapture() {
  // console.log("preCapture")
  loading_precapture.value = true
  const res = await sendPreCapture(props.full_main.id)
  loading_precapture.value = false
  mixMentions(res.pre_mentions)
}

watch(
  props.full_main.files, (newVal) => {
    note_files.value = newVal || []
  }, {immediate: true}
)

function mixMentions(pre_mentions=null) {
  if (pre_mentions) {
    props.full_main.pre_mentions = pre_mentions
  }
  const mixed_mentions = orderMix(
    props.full_main.mentions || [],
    props.full_main.pre_mentions || [],
    1
  )
  console.log("mixed_mentions\n", mixed_mentions)
  all_mentions.value = mixed_mentions
}

onMounted(() => {
  mixMentions()
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

async function discardPreMention(pre_item, index) {
  if (pre_item.discarded === true) {
    all_mentions.value[index].hide_mention = true
    return
  }
  const saved_pre_item = await discardPreItem(
    pre_item.path, props.full_main.id)
  all_mentions.value.splice(index, 1)
  // console.log("saved_pre_item", saved_pre_item)
  all_mentions.value.push(saved_pre_item)
  showSnackbar('Se ha descartado la mención preliminar')
}

async function changePreMention(pre_item, project) {
  const params = {
    project: project.id,
    note: props.full_main.id,
  }
  const index = all_mentions.value.findIndex(item =>
    item.path === pre_item.path)
  const mixed_mention = await savePreItem(
    pre_item.path, 'mention', props.full_main.id, params)
  showSnackbar('Se ha aceptado la mención preliminar')
  all_mentions.value.splice(index, 1, mixed_mention)
}

function saveMention(mention) {
  const index = all_mentions.value.findIndex(
    item => item.id === mention.id)
  all_mentions.value.splice(index, 1, mention)
  showSnackbar('Se ha guardado la mención')
}

function deleteMention(mention_id) {
  const index = all_mentions.value.findIndex(
    item => item.id === mention_id)
  if (index > -1) {
    all_mentions.value.splice(index, 1)
  }
  showSnackbar('Se ha eliminado la mención')
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

const two_columns = ref(true)

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
        elevation="3"
        variant="elevated"
        color="brown-lighten-4"
      >
        <FilesToolbar
          v-model="note_files"
          :parent_id="full_main.id"
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
          :two_columns="two_columns"
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
      <v-card v-if="all_mentions" elevation="3">
        <v-card-title>
          <div class="d-flex">
            {{ all_mentions.length }} menciones de proyectos
            <v-spacer></v-spacer>
            <v-btn
              v-if="all_mentions.length === 0"
              @click="preCapture"
              color="accent"
              class="text-none mr-2"
              variant="elevated"
              :loading="loading_precapture"
              append-icon="wand_shine"
              text="Precapturar con IA"
            ></v-btn>
            <v-btn
              @click="addMention"
              color="accent"
              variant="outlined"
              append-icon="add"
              text="Agregar mención"
            ></v-btn>
          </div>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col
              cols="12"
              v-for="(mention, idx) in all_mentions"
              :key="idx"
            >
              <v-card
                v-if="mention.hide_mention && mention.discarded === true"
                class="pa-3 d-flex align-center"
                variant="tonal"
                color="red-lighten-4"
              >
                <div class="text-title-large">
                  Mención de "{{mention.project_full.name}}" descartada
                </div>
                <v-spacer></v-spacer>
                <v-btn
                  class="ml-3"
                  color="accent "
                  variant="outlined"
                  @click="mention.hide_mention = false"
                >
                  Mostrar mención
                </v-btn>
              </v-card>

              <MentionDetails
                v-else
                v-model="all_mentions[idx]"
                ref="mentionDetailsRef"
                :full_article="full_main.articles.length > 0 ? full_main.articles[0] : null"
                :note_id="full_main.id"
                is_full
                :two_columns="two_columns"
                @mention-saved="saveMention"
                @mention-deleted="deleteMention"
                @mention-accepted="changePreMention(mention, $event)"
                @mention-discarded="discardPreMention(mention, idx)"
              />
            </v-col>
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
              <div class="text-title-large">

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