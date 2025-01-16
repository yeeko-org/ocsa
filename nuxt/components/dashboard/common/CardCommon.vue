<script setup>

import {shallowRef} from "vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import DialogEdit from "~/components/dashboard/common/DialogEdit.vue";
import { getElement } from "~/composables/save_elements.js";

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

const emits = defineEmits(['selected-item', 'delete-item'])

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
}

function closeChangeDialog(new_item) {
  if (new_item)
    emits('selected-item', new_item)
  dialog_search.value = false
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
      class="d-flex align-center"
      v-if="false"
    >
      <v-btn
        color="accent"
        variant="text"
        icon
        class="mr-2"
      >
        <v-icon>visibility</v-icon>
      </v-btn>
      <v-btn
        @click="emits('selected-item', full_main)"
        color="accent"
        variant="outlined"
      >
        Seleccionar
      </v-btn>
    </div>
    <div
      class="d-flex align-center"
      :class="{'flex-column': !is_simple && !is_select}"
    >
      <template v-if="full_main">
        <v-btn
          icon="edit"
          size="small"
          color="accent"
          :variant="is_select ? 'text' : 'outlined'"
          @click="editItem(full_main)"
          class="mr-1"
        ></v-btn>
        <v-btn
          v-if="null_available"
          icon="delete"
          size="small"
          color="error"
          variant="outlined"
          @click="emits('delete-item', full_main)"
          class="mr-1"
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
        v-else
        icon="cached"
        size="small"
        color="accent"
        variant="outlined"
        @click="searchItem"
        class="mr-1"
      ></v-btn>
    </div>
    <v-dialog
      v-model="dialog_search"
      max-width="920"
    >
      <v-card height="800">
        <v-card-text class="py-0">
          <CollectionDisplay
            :parent_collection="collection_data"
            is_mini
            @select-item="closeChangeDialog"
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