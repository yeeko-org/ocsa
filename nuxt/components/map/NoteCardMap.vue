<script setup>
import {useMainStore} from "~/store/index.js";

import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";
import ProjectMiniCard from "~/components/map/ProjectMiniCard.vue";
import MentionBodyMap from "~/components/map/MentionBodyMap.vue";

const mainStore = useMainStore()
const { getSimple } = mainStore

const props = defineProps({
  note: {
    type: Object,
    default: null,
  },
  current_project_id: Number,
})

const dialog = defineModel({type: Boolean, required: true})
const full_note = ref(null)
const loading = ref(false)

async function fetchNote() {
  if (!props.note?.id) return
  loading.value = true
  full_note.value = null
  const res = await getSimple(['note_map', props.note.id])
  full_note.value = res
  loading.value = false
}

watch(
  () => [dialog.value, props.note?.id],
  ([open, id]) => {
    if (open && id) fetchNote()
    else if (!open) full_note.value = null
  }
)

const ordered_mentions = computed(() => {
  if (!full_note.value?.mentions)
    return {main: null, others: []}
  const all = full_note.value.mentions
  const main = all.find(
    m => m.project === props.current_project_id) || null
  const others = all.filter(m => m !== main)
  return {main, others}
})
</script>

<template>
  <v-dialog v-model="dialog" max-width="720" scrollable>
    <v-card v-if="note" max-height="85vh">
      <v-card-title
        class="d-flex align-start py-2 px-3 bg-deep-purple-lighten-5"
      >
        <NoteTitle :main="note" forced_title />
        <v-spacer></v-spacer>
        <v-btn
          icon="close"
          variant="text"
          size="small"
          @click="dialog = false"
        ></v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="py-3 px-2">
        <div
          v-if="loading"
          class="d-flex justify-center align-center py-8"
        >
          <v-progress-circular indeterminate color="deep-purple" />
        </div>

        <template v-else-if="full_note">
          <v-card
            v-if="ordered_mentions.main"
            variant="outlined"
            color="deep-purple"
            class="mb-3 pa-2"
          >
            <ProjectMiniCard
              :full_main="ordered_mentions.main.project_full"
            />
            <MentionBodyMap :mention="ordered_mentions.main" />
          </v-card>

          <template v-if="ordered_mentions.others.length > 0">
            <div class="text-subtitle-2 text-grey-darken-1 mb-2 ml-1">
              Otras menciones en esta nota:
            </div>
            <v-expansion-panels variant="accordion">
              <v-expansion-panel
                v-for="mention in ordered_mentions.others"
                :key="mention.id"
              >
                <v-expansion-panel-title>
                  <ProjectMiniCard
                    :full_main="mention.project_full"
                    from_parent_project
                  />
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <MentionBodyMap :mention="mention" />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </template>
        </template>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>