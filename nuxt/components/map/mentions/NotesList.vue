<script setup>

import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";
import NoteCard from "~/components/map/mentions/NoteCard.vue";

const props = defineProps({
  full_main: {
    type: Object,
    default: null,
  },
  selectedProject: {
    type: Object,
    default: null,
  },
});

const showing = ref(10)

const related_notes = computed(() => {
  const notes = []
  const note_ids = new Set()
  if (!props.full_main?.mentions)
    return notes
  const is_grouper = props.selectedProject?.project?.is_grouper || false
  const project_id = props.selectedProject?.project?.id
  props.full_main.mentions.forEach(mention => {
    if (note_ids.has(mention.note))
      return
    note_ids.add(mention.note)
    // En grouper solo cuentan las menciones del proyecto seleccionado
    if (is_grouper && mention.project !== project_id)
      return
    notes.push(mention.note_full)
  })
  return notes
})

const filtered_notes = computed(() => {
  return related_notes.value.slice(0, showing.value)
})

const plural_comp = computed(() => {
  return related_notes.value.length !== 1 ? 's' : ''
})

const note_dialog = ref(false)
const selected_note = ref(null)

function openNoteDialog(note) {
  selected_note.value = note
  note_dialog.value = true
}

</script>

<template>
  <span class="text-title-medium text-deep-purple mt-2 ml-1">
    Mencionado directamente en {{related_notes.length}}
    nota{{plural_comp}}:
  </span>
  <v-card
    :key="note_id.id"
    v-for="note_id in filtered_notes"
    class="mb-2 py-1 px-1"
    variant="tonal"
    color="purple"
    v-ripple
    style="cursor: pointer;"
    @click="openNoteDialog(note_id)"
  >
    <NoteTitle
      :main="note_id"
      forced_title
    />
  </v-card>
  <v-card-actions class="py-0">
    <v-spacer></v-spacer>
    <v-btn
      v-if="related_notes.length > showing"
      variant="outlined"
      color="purple"
      @click="showing += 15"
      append-icon="expand_more"
    >
      Mostrar más
    </v-btn>
    <v-btn
      v-if="showing > 10"
      variant="text"
      color="red"
      @click="showing = 10"
      append-icon="expand_less"
    >
      Mostrar menos
    </v-btn>
    <v-spacer></v-spacer>
  </v-card-actions>

  <NoteCard
    v-model="note_dialog"
    :note="selected_note"
    :current_project_id="selectedProject?.project?.id"
  />
</template>