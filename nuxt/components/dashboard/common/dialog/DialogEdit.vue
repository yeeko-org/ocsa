<script setup>

import EditCommon from "~/components/dashboard/common/generic/EditCommon.vue"
import MassiveEdit from "~/components/dashboard/common/MassiveEdit.vue"
import PanelList from "~/components/dashboard/common/main/PanelList.vue"
import {shallowRef} from "vue"

const props = defineProps({
  collection_data: {type: Object, required: true},
  edit_type: {
    type: Object,
    default: () => ({key: 'edit', title: null, btn: 'Guardar'}),
  },
  selected_results: {type: Array, default: () => []},
  ids_to_edit: {type: Array, default: () => []},
  show_sheet: {type: Boolean, default: false},
})

const full_main = defineModel({type: Object, default: null})
const is_open = defineModel('open', {type: Boolean, default: false})

const emits = defineEmits([
  'close-dialog', 'item-saved', 'merge-items', 'massive-finish'])

const edit_component = shallowRef('')
const sheet_component = shallowRef('')
const editCommonRef = ref(null)

const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const edit_name = computed(() => `${props.collection_data.model_name}Edit`)
const sheet_name = computed(
    () => `${props.collection_data.model_name}Sheet`)

const title = computed(() => {
  if (props.edit_type.title) return props.edit_type.title
  return full_main.value?.id
    ? `Editar ${props.collection_data.name}`
    : `Agregar ${props.collection_data.name}`
})

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${edit_name.value}.vue`)
  .then(module => {
    edit_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/common/generic/EditGeneric.vue`)
      .then(module => {
        edit_component.value = module.default
      })
  })

if (props.show_sheet) {
  import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${sheet_name.value}.vue`)
    .then(module => {
      sheet_component.value = module.default
    })
    .catch(e => {
      import(`~/components/dashboard/common/generic/SheetCommon.vue`)
        .then(module => {
          sheet_component.value = module.default
        })
    })
}

function closeDialog() {
  is_open.value = false
  emits('close-dialog')
}

function finishSave() {
  editCommonRef.value?.finishSave()
}

defineExpose({finishSave})

</script>

<template>
  <v-dialog v-model="is_open" max-width="1200">
    <v-card v-if="full_main">
      <v-card-title class="text-headline-small d-flex">
        {{ title }}
        <v-spacer></v-spacer>
        <v-btn
          icon="close"
          variant="text"
          @click="closeDialog"
        ></v-btn>
      </v-card-title>
      <v-card-text class="py-0 px-2">
        <MassiveEdit
          v-if="edit_type.key === 'massive_edit'"
          v-model="full_main"
          :collection_data="collection_data"
          :ids_to_edit="ids_to_edit"
          @massive-finish="emits('massive-finish')"
        />
        <EditCommon
          v-else
          v-model="full_main"
          :collection_data="collection_data"
          :edit_type="edit_type"
          in_dialog
          ref="editCommonRef"
          @item-saved="emits('item-saved', $event)"
          @merge-items="emits('merge-items', $event)"
        >
          <template #edit v-if="edit_component">
            <component
              :is="edit_component"
              v-model="full_main"
              :is_edit="!!full_main?.id"
            />
          </template>
        </EditCommon>
        <template v-if="edit_type.key !== 'edit' && selected_results.length">
          <v-divider></v-divider>
          <PanelList
            :results="selected_results"
            :collection_data="collection_data"
            :show_details="true"
          />
        </template>
        <component
          v-if="show_sheet && sheet_component"
          :is="sheet_component"
          :full_main="full_main"
          :show_details="true"
          :collection_data="collection_data"
        />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>