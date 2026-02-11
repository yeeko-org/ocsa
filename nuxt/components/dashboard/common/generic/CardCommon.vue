<script setup>

import DialogEdit from "~/components/dashboard/common/dialog/DialogEdit.vue";
import {getElement} from "~/composables/save_elements.js";
import ParagraphFilter from "~/components/dashboard/capture/ParagraphFilter.vue";
import { useMainStore } from "~/store/index.js";
const mainStore = useMainStore()
import {storeToRefs} from "pinia";
import DialogSearch from "~/components/dashboard/common/dialog/DialogSearch.vue";
import CardComponent from "~/components/dashboard/common/CardComponent.vue";
const { content_paragraphs, schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: Object,
  collection_data: Object,
  collection_name: String,
  is_simple: Boolean,
  title: String,
  indirect_get: Boolean,
  null_available: Boolean,
  is_select: Boolean,
  note_id: Number,
  disabled_discard_buttons: Boolean,
  // full_article: Object,
  init_filters: {
    type: Object,
    default: () => ({}),
  },
})

const final_collection_data = computed(() => {
  if (props.collection_data)
    return props.collection_data
  return schemas.value.collections_dict[props.collection_name]
})


const dialog_edit = ref(false)
const elem_in_edition = ref(null)

function editItem(item) {
  // console.log("editItem", item)
  base_element.value = false
  if (props.indirect_get || props.is_select){
    getElement(final_collection_data.value, item.id).then(response => {
      elem_in_edition.value = response
      dialog_edit.value = true
    })
  }
  else{
    elem_in_edition.value = item
    dialog_edit.value = true
  }
}

const emits = defineEmits([
  'selected-item', 'delete-item', 'edit-item', 'discard-item'])

function closeDialog(event) {
  // console.log("close dialog", event)
  dialog_edit.value = false
  if (!event) return
  emits('selected-item', event)
}

const dialog_search = ref(false)
const base_element = ref(false)
function searchItem(full_project = false) {
  // console.log("search item")
  // console.log("init filters", props.init_filters)
  base_element.value = full_project
  dialog_search.value = true
  if (full_project){
    const paragraphs = props.full_main?.paragraphs || []
    if (!props.note_id) return
    if (paragraphs.length === 0) return
    nextTick(() => {
      if (!props.note_id)
        return
      content_paragraphs.value = {
        paragraphs: paragraphs,
        note_id: props.note_id,
        path: props.full_main?.path,
        is_active: true,
      }
  })
  }
}

function closeSearchDialog(new_item) {
  if (new_item)
    emits('selected-item', new_item)
  dialog_search.value = false
}

</script>

<template>
  <v-card
    class="d-flex align-center px-3"
    :color="final_collection_data.color"
    variant="tonal"
    style="width: 100%;"
  >
<!--    <component-->
<!--      v-if="card_component && full_main"-->
<!--      :is="card_component"-->
<!--      :full_main="full_main"-->
<!--      :title="title"-->
<!--    />-->
    <slot
      name="card"
      v-if="full_main"
      :final_collection_data="final_collection_data"
    >
      <CardComponent
        :full_main="full_main"
        :collection_data="final_collection_data"
        :title="title"
        :note_id="note_id"
      />
    </slot>
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
          @click="searchItem(true)"
          :disabled="disabled_discard_buttons"
          v-tooltip="`Aceptar y elegir ${final_collection_data.name}`"
        ></v-btn>
        <v-btn
          v-if="null_available"
          icon="delete"
          size="small"
          color="error"
          variant="outlined"
          @click="emits('delete-item', full_main)"
          class="mr-1"
          :disabled="disabled_discard_buttons"
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
        :disabled="disabled_discard_buttons"
        v-tooltip="`Descartar ${final_collection_data.name}`"
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
      <ParagraphFilter
        :paragraphs="full_main?.paragraphs"
        :note_id="note_id"
        :path="full_main?.path || full_main?.sub_path"
      />
    </div>
<!--    <v-dialog-->
<!--      v-model="dialog_search"-->
<!--      max-width="920"-->
<!--    >-->
<!--      <v-card height="840">-->
<!--        <v-card-text class="py-0">-->
<!--          <CollectionDisplay-->
<!--            :parent_collection="collection_data"-->
<!--            is_mini-->
<!--            @select-item="closeChangeDialog"-->
<!--            :init_filters="init_filters"-->
<!--          />-->
<!--        </v-card-text>-->
<!--      </v-card>-->
<!--    </v-dialog>-->
    <v-dialog
      v-model="dialog_search"
      max-width="1420"
    >
      <slot name="dialog" :closeSearchDialog="closeSearchDialog">
        <DialogSearch
          :collection_data="final_collection_data"
          :init_filters="init_filters"
          @selected-item="closeSearchDialog"
        />
      </slot>
    </v-dialog>
    <v-dialog
      v-model="dialog_edit"
      max-width="1200"
    >
      <DialogEdit
        v-model="elem_in_edition"
        :collection_data="final_collection_data"
        @close-dialog="closeDialog($event)"
      />
    </v-dialog>
  </v-card>
</template>
