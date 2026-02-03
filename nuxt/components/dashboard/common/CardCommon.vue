<script setup>

import {shallowRef} from "vue";
import {storeToRefs} from "pinia";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import DialogEdit from "~/components/dashboard/common/DialogEdit.vue";
import { getElement } from "~/composables/save_elements.js";
import { useMainStore } from "~/store/index.js";
const mainStore = useMainStore()
const { content_paragraphs } = storeToRefs(mainStore)

const props = defineProps({
  full_main: Object,
  collection_data: {
    type: Object,
    required: true,
  },
  is_simple: Boolean,
  title: String,
  indirect_get: Boolean,
  null_available: Boolean,
  is_select: Boolean,
  note_id: Number,
  project_id: Number,
  init_filters: {
    type: Object,
    default: () => ({}),
  },
})

const card_component = shallowRef('')
const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const card_name = computed(() => `${props.collection_data.model_name}Card`)

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${card_name.value}.vue`)
  .then(module => {
    card_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/CardGeneric.vue`).then(module => {
      card_component.value = module.default
    })
  })

const emits = defineEmits([
  'selected-item', 'delete-item', 'edit-item', 'discard-item'])

const dialog_search = ref(false)
const dialog_edit = ref(false)
const elem_in_edition = ref(null)

function editItem(item) {
  // console.log("editItem", item)
  if (props.indirect_get || props.is_select){
    getElement(props.collection_data, item.id).then(response => {
      elem_in_edition.value = response
      dialog_edit.value = true
    })
  }
  else{
    elem_in_edition.value = item
    dialog_edit.value = true
  }
}

function searchItem() {
  dialog_search.value = true
}

function closeDialog(event) {
  // console.log("close dialog", event)
  dialog_edit.value = false
  emits('selected-item', event)
}

function closeChangeDialog(new_item) {
  if (new_item)
    emits('selected-item', new_item)
  dialog_search.value = false
}

const paragraphs_active = computed(() => {
  return content_paragraphs.value &&
    content_paragraphs.value.note_id === props.note_id
})

function filterParagraphs() {
  if (!props.note_id || !props.full_main.paragraphs)
    return
  if (paragraphs_active.value) {
    content_paragraphs.value = {is_reset: true}
    return
  }

  content_paragraphs.value = {
    paragraphs: props.full_main.paragraphs,
    note_id: props.note_id,
    project_id: props.project_id,
  }
}

</script>

<template>
  <v-card
    class="d-flex align-center px-3"
    :color="collection_data.color"
    variant="tonal"
    style="width: 100%;"
  >
    <component
      v-if="card_component && full_main"
      :is="card_component"
      :full_main="full_main"
      :title="title"
    />
    <span v-else class="text-h6 mr-2 text-warning">
      Sin {{title || collection_data.name}}
    </span>
    <v-spacer></v-spacer>
    <div
      class="d-flex align-center ga-1"
      :class="{'flex-column': !is_simple && !is_select}"
    >
      <template v-if="full_main">
        <v-btn
          v-if="full_main.id"
          icon="edit"
          size="small"
          color="accent"
          :variant="is_select ? 'text' : 'outlined'"
          @click="editItem(full_main)"
          class="mr-1"
          v-tooltip="`Editar`"
        ></v-btn>
        <v-btn
          v-else-if="!full_main.id"
          icon="done_outline"
          size="small"
          color="success"
          variant="outlined"
          @click="searchItem"
          v-tooltip="`Aceptar y elegir ${collection_data.name}`"
        ></v-btn>
        <v-btn
          v-if="null_available"
          icon="delete"
          size="small"
          color="error"
          variant="outlined"
          @click="emits('delete-item', full_main)"
          class="mr-1"
          v-tooltip="`Eliminar`"
        ></v-btn>
      </template>
      <v-btn
        v-if="is_select"
        @click="emits('selected-item', full_main)"
        color="accent"
        variant="outlined"
      >
        Seleccionar
      </v-btn>
      <v-btn
        v-else-if="full_main && !full_main.id"
        icon="close"
        size="small"
        color="error"
        variant="outlined"
        @click="emits('discard-item')"
        v-tooltip="`Rechazar ${collection_data.name}`"
      ></v-btn>
      <v-btn
        v-else
        icon="cached"
        size="small"
        color="accent"
        variant="outlined"
        @click="searchItem"
        class="mr-1"
        v-tooltip="`Cambiar`"
      ></v-btn>
      <v-btn
        v-if="full_main.paragraphs"
        icon
        size="small"
        color="accent"
        :variant="paragraphs_active ? 'elevated' : 'text'"
        @click="filterParagraphs()"
        v-tooltip="`Filtrar párrafos`"
      >
        <v-icon size="large">filter_list</v-icon>
      </v-btn>
    </div>
    <v-dialog
      v-model="dialog_search"
      max-width="920"
    >
      <v-card height="840">
        <v-card-text class="py-0">
          <CollectionDisplay
            :parent_collection="collection_data"
            is_mini
            @select-item="closeChangeDialog"
            :init_filters="init_filters"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialog_edit">
      <DialogEdit
        :full_main="elem_in_edition"
        :collection_data="collection_data"
        @close-dialog="closeDialog($event)"
      />
    </v-dialog>
  </v-card>
</template>

<style scoped>

</style>