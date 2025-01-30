<script setup>

import EditCommon from "~/components/dashboard/common/EditCommon.vue";
import {shallowRef} from "vue";

const props = defineProps({
  collection_data: Object,
  full_main: {
    type: Object,
    required: true,
  },
})

const edit_component = shallowRef('')
const sheet_component = shallowRef('')
const emits = defineEmits(['close-dialog'])
const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const edit_name = computed(() => `${props.collection_data.model_name}Edit`)
const sheet_name = computed(() => `${props.collection_data.model_name}Sheet`)


import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${edit_name.value}.vue`)
  .then(module => {
    edit_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/EditGeneric.vue`).then(module => {
      edit_component.value = module.default
    })
  })

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${sheet_name.value}.vue`)
  .then(module => {
    sheet_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/SheetCommon.vue`).then(module => {
      sheet_component.value = module.default
    })
  })

function saveItem({res, is_new}) {
  console.log('saveItem', res, is_new)
  emits('close-dialog', res)
}

</script>

<template>
  <v-card>
    <v-card-title class="text-h5 d-flex">
      <span v-if="!full_main.id">
        Crear {{collection_data.name}}
      </span>
      <span v-else>
        Editar {{collection_data.name}}
      </span>
      <v-spacer></v-spacer>
      <v-btn
        icon="close"
        variant="text"
        @click="emits('close-dialog')"
      >
      </v-btn>
    </v-card-title>
    <v-card-text class="py-0 px-2">
      <EditCommon
        :full_main="full_main"
        :collection_name="collection_data.snake_name"
        @item-saved="saveItem"
      >
        <template #edit="{ full_main }" v-if="edit_component">
          <component
            :is="edit_component"
            :full_main="full_main"
            is_edit
          />
        </template>
        <template
          #sheet="{full_main}"
          v-if="sheet_component"
        >
          <component
            :is="sheet_component"
            :full_main="full_main"
            :show_details="true"
            :collection_data="collection_data"
          />
        </template>
      </EditCommon>

      <component
        v-if="sheet_component"
        :is="sheet_component"
        :full_main="full_main"
        :show_details="true"
        :collection_data="collection_data"
      />
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>