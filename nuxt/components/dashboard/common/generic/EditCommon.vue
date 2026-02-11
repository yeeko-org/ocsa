<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {useDashboardStore} from "~/store/dash.js";
import EditCommonFields from "~/components/dashboard/common/generic/EditCommonFields.vue";
import AlertInfo from "~/components/dashboard/common/utils/AlertInfo.vue";

const mainStore = useMainStore()
const dashboardStore = useDashboardStore()
import { saveElement, deleteElement } from "~/composables/save_elements.js";
const { schemas, status_dict } = storeToRefs(mainStore)
const { showSnackbar } = dashboardStore
import {status_filters} from "~/composables/filters.js";

const props = defineProps({
  // full_main: Object,
  collection_data: Object,
  collection_name: String,
  can_delete: Boolean,
  in_dialog: Boolean,
  edit_type: {
    type: Object,
    default: () => ({key: 'edit', title: 'Agregar Registro', btn: 'Guardar'})
  },
})
const full_main = defineModel({type: Object, required: true})

const saving = ref(false)
const deleting = ref(false)
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
  if (!full_main.value.id && !full_main.value.comments){
    const coll = final_collection_data.value
    if (coll.is_category && coll.has.comments) {
      errors.value = "Cuando creas una categoría, debes añadir un comentario " +
        "para explicar la razón de su creación"
      return
    }
  }
  saving.value = true
  const elem_id = final_collection_data.value.pk
  let is_new = true
  if (elem_id === 'id')
    is_new = !full_main.value.id
  else if (elem_id === 'key_name')
    is_new = full_main.value.is_new === true
  saveElement(final_collection_data.value, full_main.value).then((res) => {
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

function finishSave(snackbar_msg='Se ha guardado el registro'){
  saving.value = false
  showSnackbar(snackbar_msg)
}

function updateStatus({status_group, new_status, res}){
  const status_key = status_group.replace('status_', '')
  const new_status_obj = status_dict.value[status_key][new_status]
  const status_info = status_filters[status_group]
  // console.log('status_info', status_info)
  const msg = `Status ${status_info.name} actualizado
    a "${new_status_obj.public_name}"`
  finishSave(msg)
  if (!props.in_dialog)
    emits('item-saved', {res, is_new: false})
}

function updateComments(res){
  finishSave('Comentarios guardados correctamente')
  if (!props.in_dialog)
    emits('item-saved', {res, is_new: false})
}

function deleteRecord() {
  errors.value = null
  deleting.value = true
  const id_to_delete = full_main.value[props.collection_data.pk]
  deleteElement(final_collection_data.value, id_to_delete)
    .then((res) => {
      if (res.errors) {
        // const error_msg = "No se pudo eliminar el registro si tiene datos relacionados"
        // errors.value = `${error_msg}: \n${
        //   JSON.stringify(res.errors.report_data)}`
        let error_msg = "No se pudo eliminar el registro:\n"
        error_msg += JSON.stringify(res.errors)
        errors.value = error_msg
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
      style="white-space: pre-wrap;"
    >
      {{errors}}
    </v-alert>
    <AlertInfo
      :help_text="final_collection_data.help_text"
      class="mb-3"
    />
    <v-form
      ref="editForm"
    >
      <EditCommonFields
        v-model="full_main"
        :final_collection_data="final_collection_data"
        @update-status="updateStatus($event)"
        @update-comments="updateComments($event)"
      >
        <template #edit>
          <slot name="edit">
            EDICIÓN 1 (REPORTAR SI APARECE PORQUE PORQUE NO ES NORMAL)
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
            Sí eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style scoped>

</style>