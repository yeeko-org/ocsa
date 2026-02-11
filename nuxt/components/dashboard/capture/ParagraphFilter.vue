<script setup>


import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
import {storeToRefs} from "pinia";

const { content_paragraphs } = storeToRefs(mainStore)

const props = defineProps({
  paragraphs: {
    type: Array,
    default: () => [],
  },
  note_id: Number,
  path: {
    type: String,
    default: 'generic',
  },
})

const paragraphs_active = computed(() => {
  return content_paragraphs.value
    && content_paragraphs.value.note_id === props.note_id
    && content_paragraphs.value.path === props.path
})

function filterParagraphs() {
  if (!props.note_id)
    return
  if (paragraphs_active.value) {
    content_paragraphs.value = {is_reset: true}
    return
  }

  content_paragraphs.value = {
    paragraphs: props.paragraphs,
    note_id: props.note_id,
    path: props.path,
    is_active: true,
  }
  // console.log("filterParagraphs", content_paragraphs.value)
}

</script>

<template>
  <v-btn
    v-if="paragraphs.length > 0"
    icon
    size="small"
    color="accent"
    :variant="paragraphs_active ? 'elevated' : 'text'"
    @click="filterParagraphs"
  >
    <v-icon size="large">filter_list</v-icon>
    <v-tooltip
      activator="parent"
      location="top"
    >
      <span v-if="!paragraphs_active">
        Filtrar párrafos asociados
        <br> Elemento: {{ path }}
      </span>
      <span v-else>
        Desactivar filtro de párrafos
      </span>
    </v-tooltip>
  </v-btn>
</template>