<script setup>
import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";
import NoteCardMap from "~/components/map/NoteCardMap.vue";

const props = defineProps({
  type_elem: {
    type: Object,
    default: null,
  },
  group: {
    type: Object,
    default: null,
  },
  filter_objects: {
    type: Array,
    default: () => [],
  },
  mentions: {
    type: Array,
    default: () => [],
  },
  current_project_id: Number,
})

const dialog = defineModel({type: Boolean, required: true})

const note_dialog = ref(false)
const selected_note = ref(null)

const notes_with_snippets = computed(() => {
  if (!props.filter_objects?.length || !props.mentions?.length)
    return []
  const mentions_index = {}
  props.mentions.forEach(m => {
    mentions_index[m.id] = m
  })
  const map = new Map()
  props.filter_objects.forEach(obj => {
    const mention = mentions_index[obj.mention]
    if (!mention?.note_full) return
    const note = mention.note_full
    if (!map.has(note.id)) {
      map.set(note.id, {note, snippets: []})
    }
    map.get(note.id).snippets.push({
      id: obj.id,
      description: obj.description || 'Sin descripción',
    })
  })
  return [...map.values()].sort(
    (a, b) => b.snippets.length - a.snippets.length)
})

function openNote(note) {
  selected_note.value = note
  note_dialog.value = true
}
</script>

<template>
  <v-dialog v-model="dialog" max-width="720" scrollable>
    <v-card v-if="type_elem && group" max-height="85vh">
      <v-card-title
        class="py-2 px-3"
        :class="`bg-${group.color}-lighten-4`"
      >
        <div class="d-flex align-center mb-1">
          <v-icon :color="group.color" class="mr-2">
            {{ group.icon }}
          </v-icon>
          <span class="text-subtitle-2 text-grey-darken-2">
            {{ group.title }}
          </span>
          <v-spacer></v-spacer>
          <v-btn
            icon="close"
            variant="text"
            size="small"
            @click="dialog = false"
          ></v-btn>
        </div>
        <div class="text-h6 font-weight-bold">
          {{ type_elem.name }}
        </div>
        <div
          v-if="type_elem.description"
          class="text-body-2 text-grey-darken-1 mt-1"
          style="white-space: normal;"
        >
          {{ type_elem.description }}
        </div>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="py-3 px-2">
        <div
          v-if="notes_with_snippets.length === 0"
          class="text-body-2 text-grey text-center py-4"
        >
          No hay notas asociadas.
        </div>
        <v-card
          v-for="entry in notes_with_snippets"
          :key="entry.note.id"
          variant="tonal"
          color="purple"
          class="mb-2 px-2 py-2"
          v-ripple
          style="cursor: pointer;"
          @click="openNote(entry.note)"
        >
          <NoteTitle :main="entry.note" forced_title />
          <div class="pl-2 mt-1">
            <div
              v-for="(snippet, idx) in entry.snippets"
              :key="snippet.id || idx"
              class="text-body-2 d-flex align-start mb-1"
            >
              <v-icon size="x-small" class="mr-1 mt-1">
                fiber_manual_record
              </v-icon>
              <span>{{ snippet.description }}</span>
            </div>
          </div>
        </v-card>
      </v-card-text>
    </v-card>
    <NoteCardMap
      v-model="note_dialog"
      :note="selected_note"
      :current_project_id="current_project_id"
    />
  </v-dialog>
</template>

<style scoped>

</style>