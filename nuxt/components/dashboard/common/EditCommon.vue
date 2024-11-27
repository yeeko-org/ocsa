<script setup>

import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import Comments from "~/components/dashboard/common/Comments.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {saveElement} from "~/composables/save_elements.js";
// import {saveElement} from "~/composables/save_elements.js";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: Object,
  collection_data: Object,
  collection_name: String,
})

const saving = ref(false)
const snackbar = ref(false)
const emits = defineEmits(['new-item'])

const final_collection_data = computed(() => {
  if (props.collection_data)
    return props.collection_data
  return schemas.value.collections_dict[props.collection_name]
})

function saveRecord() {
  // emits('save-item', props.full_main)
  saving.value = true
  const elem_id = props.full_main.id ? 'id' : 'key_name'
  // console.log('props.full_main', props.full_main)
  const is_new = !Boolean(props.full_main[elem_id])
  saveElement(final_collection_data.value, props.full_main).then((res) => {
    emits('item-saved', {res, is_new})
    snackbar.value = true
    saving.value = false
  })
}

</script>

<template>
  <v-card class="mb-3 pa-3" elevation="8">
    <v-card-text
      class="d-flex flex-wrap"
    >
      <v-col cols="12" class="d-flex pa-0">
        <v-text-field
          v-if="final_collection_data.has.order"
          v-model="full_main.order"
          label="Orden"
          type="number"
          variant="outlined"
          class="mr-2"
          style="max-width: 70px;"
        >
        </v-text-field>
        <v-text-field
          v-if="final_collection_data.name_field"
          v-model="full_main[final_collection_data.name_field]"
          label="Nombre"
          class="mr-2"
          variant="outlined"
          style="width: 300px;"
        />
        <v-spacer></v-spacer>
        <template v-if="final_collection_data.status_groups">
          <StatusDetail
            v-for="status_group in final_collection_data.status_groups"
            :final_filters="full_main"
            :collection="status_group"
            style="max-width: 300px;"
            density="default"
            class="mr-1"
          />
        </template>
        <Comments
          v-if="final_collection_data.has.comments"
          :main="full_main"
          :final_collection_data="final_collection_data"
        />
      </v-col>
      <slot name="edit" :full_main="full_main">
        EDICIÓN (REVISAR PORQUE NO ES NORMAL)
      </slot>
      <v-col
        v-if="final_collection_data.has.description"
        cols="12"
        class="d-flex pa-0"
      >
        <v-textarea
          v-model="full_main.description"
          label="Descripción"
          rows="1"
          auto-grow
          class="mr-2"
          variant="outlined"
        ></v-textarea>
      </v-col>
      <v-col
        cols="12"
        class="d-flex pa-0"
      >
        <v-textarea
          v-if="final_collection_data.has.help_text"
          v-model="full_main.help_text"
          label="Texto de ayuda"
          variant="outlined"
          rows="2"
          auto-grow
          _hide-details
        >
        </v-textarea>
      </v-col>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        color="accent"
        variant="elevated"
        :loading="saving"
        @click="saveRecord"
      >
        Guardar
      </v-btn>
    </v-card-actions>

    <v-snackbar
      v-model="snackbar"
      color="success"
      location="right top"
      location-strategy="connected"
    >
      Se ha guardado el registro
      <template v-slot:actions>
        <v-btn
          color="accent"
          variant="text"
          @click="snackbar = false"
        >
          Cerrar
        </v-btn>
      </template>
    </v-snackbar>
  </v-card>
</template>

<style scoped>

</style>