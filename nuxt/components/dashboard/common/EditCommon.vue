<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import { saveElement, deleteElement } from "~/composables/save_elements.js";
import EditCommonFields from "~/components/dashboard/common/EditCommonFields.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: Object,
  collection_data: Object,
  collection_name: String,
  can_delete: Boolean,
  edit_type: {
    type: Object,
    default: () => ({key: 'edit', title: 'Agregar Registro', btn: 'Guardar'})
  },
})

const saving = ref(false)
const deleting = ref(false)
const snackbar = ref(false)
const editForm = ref(null)
const dialog_delete = ref(false)
const errors = ref(null)

const emits = defineEmits([
    'new-item', 'item-deleted', 'item-saved', 'merge-items'])
defineExpose({ finishSave })

const final_collection_data = computed(() => {
  if (props.collection_data)
    return props.collection_data
  return schemas.value.collections_dict[props.collection_name]
})

async function saveRecord() {
  errors.value = null
  const { valid } = await editForm.value.validate()
  if (!valid) return
  saving.value = true
  // const elem_id = props.full_main.id ? 'id' : 'key_name'
  const elem_id = final_collection_data.value.pk
  // let is_new = true
  // if (props.full_main.id)
  //   is_new = false
  // else if (props.full_main.key_name)
  //   is_new = props.full_main.is_new === true
  let is_new = true
  if (elem_id === 'id')
    is_new = !props.full_main.id
  else if (elem_id === 'key_name')
    is_new = props.full_main.is_new === true
  saveElement(final_collection_data.value, props.full_main).then((res) => {
    if (res.errors) {
      errors.value = res.errors
      saving.value = false
      return
    }
    if (props.edit_type.key === 'merge')
      emits('merge-items', res)
    else{
      emits('item-saved', {res, is_new})
      finishSave()
    }
  })
}

function finishSave(){
  saving.value = false
  snackbar.value = true
}

function deleteRecord() {
  errors.value = null
  deleting.value = true
  const id_to_delete = props.full_main[props.collection_data.pk]
  deleteElement(final_collection_data.value, id_to_delete)
    .then((res) => {
      console.log("res", res)
      if (res.errors) {
        const error_msg = "No se pudo eliminar el registro si tiene datos relacionados"
        errors.value = `${error_msg}: \n${
          JSON.stringify(res.errors.report_data)}`
        deleting.value = false
        dialog_delete.value = false
        return
      }
      deleting.value = false
      dialog_delete.value = false
      emits('item-deleted', id_to_delete)
    })
}

</script>

<template>
  <v-card class="mb-3 pa-3" elevation="8">
    <v-alert
      v-if="errors"
      type="error"
      dismissible
      elevation="2"
      class="mb-3"
      v-html="errors"
      style="white-space: pre-wrap;"
    >
    </v-alert>
    <v-form
      ref="editForm"
    >
      <EditCommonFields
        :full_main="full_main"
        :final_collection_data="final_collection_data"
      >
        <template #edit="{ full_main }">
          <slot name="edit" :full_main="full_main">
            EDICIÓN 1 (REVISAR PORQUE NO ES NORMAL)
          </slot>
        </template>
      </EditCommonFields>
      <v-card-actions>
        <v-btn
          v-if="final_collection_data.level !== 'secondary'"
          color="error"
          variant="outlined"
          @click="dialog_delete = true"
        >
          Eliminar
        </v-btn>

        <v-btn
          v-if="final_collection_data.other_fields
            && final_collection_data.other_fields.length"
          icon
          size="small"
        >
          <v-icon>info</v-icon>
          <v-tooltip
            bottom
            activator="parent"
          >
            <span class="font-weight-bold">Todos los campos:</span>
            <div v-for="field in final_collection_data.other_fields">
              {{field.name}} -- {{field.field_type}}
            </div>
          </v-tooltip>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          :id="`save_${final_collection_data.snake_name}-${
            full_main.id || full_main.key_name || 'new'
          }`"
          color="accent"
          variant="elevated"
          :loading="saving"
          @click="saveRecord"
        >
          {{ edit_type.btn || 'Guardar' }}
        </v-btn>
      </v-card-actions>
    </v-form>
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
    <v-dialog
      v-model="dialog_delete"
      max-width="500"
    >
      <v-card class="pa-3">
        <v-card-title>
          ¿Confirmas la eliminación de este registro?
        </v-card-title>
        <v-card-subtitle>
          Esta acción no se puede deshacer
        </v-card-subtitle>
        <v-card-actions class="py-4">
          <v-btn
            color="accent"
            variant="outlined"
            @click="dialog_delete = false"
          >
            Cancelar
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-if="can_delete"
            color="error"
            variant="elevated"
            :loading="deleting"
            @click="deleteRecord"
          >
            Eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style scoped>

</style>