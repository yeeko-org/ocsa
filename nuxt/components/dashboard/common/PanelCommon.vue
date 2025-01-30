<script setup>
import {ref, computed, nextTick, shallowRef} from 'vue'
import { getElement } from "~/composables/save_elements.js";
import EditCommon from "~/components/dashboard/common/EditCommon.vue";
import { patchElement } from "~/composables/save_elements.js";

const props = defineProps({
  main: Object,
  collection_data: {
    type: Object,
    required: true,
  },
  sel: Object,
  main_action: {
    type: String,
    default: 'checkbox',
  }
})

const full_main = ref({})
const edit_component = shallowRef('')
const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const edit_name = computed(() => `${props.collection_data.model_name}Edit`)

const emits = defineEmits([
    'finish-open', 'item-saved', 'item-deleted', 'select-item'])

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${edit_name.value}.vue`)
  .then(module => {
    edit_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/EditGeneric.vue`).then(module => {
      edit_component.value = module.default
    })
  })


const openMain = () => {
  // const group = props.group
  // const real_group = group.parent ? `catalogs/${group.key}` : group.key
  const level = props.collection_data.level
  // console.log('level', level)
  if (level === 'category_group'){
    emits('finish-open')
    full_main.value = props.main
    return
  }
  const elem_id = props.main.id ? 'id' : 'key_name'
  getElement(props.collection_data, props.main[elem_id]).then((res) => {
    full_main.value = res
    emits('finish-open')
  })
}

const background_color = computed(() => {
  const coll = props.collection_data
  if (!coll)
    return 'secondary-lighten-5'
  const base_color = coll.color ||
    (coll.parent ? (coll.parent.color || 'blue-grey') : 'blue-grey')
  return `${base_color}-lighten-5`
})

const is_group = computed(() =>
  props.collection_data.level === 'category_group')

const saveOrder = (val) => {
  console.log('saveOrder', val)
  console.log('val', props.main.order)

  if (!val) return
  const params = {order: props.main.order}
  const collection = props.collection_data.snake_name
  // const collection = props.final_collection_data.snake_name
  patchElement(props.collection_data, props.main.id, params).then((res) => {
    // want_edit_comment.value = false
    console.log('order saved', res)
  })
}


</script>

<template>
  <v-expansion-panel class="d-flex">
    <v-sheet
      :color="background_color"
      class="d-flex align-start flex-shrink-0 justify-center"
    >
      <v-card
        v-if="is_group"
        variant="plain"
        color="grey-darken-1"
        class="mt-0 px-0 pt-2 pb-1 text-center"
        width="44"
      >
        <div class="text-caption">Orden:</div>
        <div>{{main.order}}</div>
      </v-card>
      <v-card
        v-else-if="main_action === 'order'"
        variant="outlined"
        color="grey-darken-1"
        class="mt-2 px-0 pt-2 pb-1"
        width="44"
      >
        <v-text-field
          v-model="main.order"
          density="compact"
          label="Orden"
          variant="plain"
          hide-details
          width="42"
          class="px-1"
          @update:model-value="saveOrder"
        ></v-text-field>
      </v-card>
      <v-checkbox
        v-else-if="sel && main_action === 'checkbox'"
        v-model="sel.selected_elems"
        :value="main[collection_data.pk]"
        _density="comfortable"
        hide-details
        class="pt-1 pl-1"
      />
      <v-btn
        v-else-if="main_action === 'click'"
        class="mt-3 ml-1"
        icon
        variant="outlined"
        size="small"
        @click="emits('select-item', main)"
      >
        <v-icon
          size="large"
        >ads_click</v-icon>
      </v-btn>
      <div v-else style="width: 40px;">

      </div>

    </v-sheet>

    <v-sheet class="flex-grow-1" :color="background_color">
      <slot name="header" :main="main" :openMain="openMain">
        <v-expansion-panel-title>
          Cargando detalles...
        </v-expansion-panel-title>
      </slot>
      <v-expansion-panel-text
        v-if="full_main"
        class="ml-n16 mr-n6"
        :color="background_color"
      >
        <v-sheet
          :color="background_color"
          class="mt-n2 mb-n4 pa-3"
        >
          <EditCommon
            :full_main="full_main"
            :collection_data="collection_data"
            @item-saved="emits('item-saved', $event)"
            @item-deleted="emits('item-deleted', $event)"
            can_delete
          >
            <template #edit="{ full_main }">
              <component
                :is="edit_component"
                :full_main="full_main"
                is_edit
              />
            </template>
          </EditCommon>
          <slot name="sheet" :full_main="full_main">
            Contenido genérico 3
          </slot>
        </v-sheet>
      </v-expansion-panel-text>
    </v-sheet>
  </v-expansion-panel>
</template>

<style scoped>

</style>