<script setup>
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {useDashboardStore} from "~/store/dash.js";
const mainStore = useMainStore()
const dashboardStore = useDashboardStore()
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

import { useSaveElements } from "~/composables/save_elements.js";
import { useDeleteWithReport } from "~/composables/delete_with_report.js";
import { savePreItem, discardPreItem, saveItemMixed } from "~/composables/mix_pre_capture.js";
import DialogDelete from "~/components/dashboard/common/dialog/DialogDelete.vue";
import ToolbarHeader from "~/components/dashboard/capture/ToolbarHeader.vue";
import DiscardButtons from "~/components/dashboard/capture/DiscardButtons.vue";
import ParagraphFilter from "~/components/dashboard/capture/ParagraphFilter.vue";
const { saveComplex, save_errors } = useSaveElements()
const {
  report_data: delete_report_data,
  deleting,
  delete_errors,
  tryDelete,
  confirmForceDelete,
  reset: resetDelete,
} = useDeleteWithReport()

const props = defineProps({
  parent_id: {
    type: Number,
    required: false,
  },
  main_collection_name: {
    type: String,
    required: false,
    default: 'mention',
  },
  filter_group_name: String,
  child_relation_name: String,
  additional_fields: Object,
  required: Boolean,
  forced_level: String,
  special_multiple: Boolean,
  second_level: Boolean,
  two_columns: Boolean,
  emit_add: Boolean,

  hide_pre_buttons: Boolean,
  note_id: Number,
  vertical_actions: Boolean,

  required_field: String,
  required_full_category: Boolean,
  cols: {
    type: Number,
    default: 12,
  },
  color: {
    type: String,
    default: 'indigo',
  },
})

const main_array = defineModel({type: Array, required: true})

const dialog_delete = ref(false)
const delete_text = ref('')
const record_to_delete = ref({})
const saving = ref(false)
const index_in_edit = ref(null)
const elem_to_save = ref(null)
const selectGroupRef = ref(null)
// const touched_index = ref({})

const { schemas } = storeToRefs(mainStore)
const { saveSimple } = mainStore
const { showSnackbar } = dashboardStore

const emits = defineEmits(['add-item'])
defineExpose({ resetInitialData, validateAllForms })

const filter_group = computed(() =>
  schemas.value.filter_groups.find(
    cat_group => cat_group.key_name === props.filter_group_name)
)

const child_collection = computed(() =>
  schemas.value.collections_dict[props.child_relation_name])

const parent_object = computed(() => {
  return {[props.main_collection_name]: props.parent_id}
})

const mainForm = ref(null)
const childValidators = ref([])

function registerChildValidator(validateFn) {
  childValidators.value.push(validateFn)
}
// function registerChildValidator(validateFn, metadata = {}) {
//   console.log("Registering child validator:", {
//     validateFn,
//     metadata
//   })
//   childValidators.value.push({validate: validateFn, ...metadata})
// }

function unregisterChildValidator(validateFn) {
  const idx = childValidators.value.indexOf(validateFn)
  if (idx !== -1) childValidators.value.splice(idx, 1)
}

provide('toolbar-register-validator', registerChildValidator)
provide('toolbar-unregister-validator', unregisterChildValidator)

const parentRegister = inject('toolbar-register-validator', null)
const parentUnregister = inject('toolbar-unregister-validator', null)

const element_errors = ref({})

function showValidationErrors(msg="Formulario no válido", index=null) {
  if (index !== null)
    element_errors.value[index] = msg
  else
    save_errors.value = [msg]
  return false
}

async function validateAllForms(index=null, only_current=false) {
  // console.log("Validating main form(s)...\n", mainForm.value)
  // console.log("Index:", index, "Only current:", only_current)
  element_errors.value = {}
  if (mainForm.value && mainForm.value.length > 0) {
    if (index === null){
      const validations = await Promise.all(
        mainForm.value.map(formRef => {
          if (formRef.class.includes('pre_item'))
            return { valid: true }
          return formRef.validate()
        })
      )
      const allValid = validations.every(result => result.valid)
      if (!allValid) return showValidationErrors(
        "Completa todos los campos requeridos")
    }
    else {
      // console.log("validating form at index", index)
      const formRef = mainForm.value[index]
      // console.log("formRef", formRef)
      if (!formRef)
        return showValidationErrors(
          "Formulario no encontrado", index)
      const { valid } = await formRef.validate()
      // console.log("valid formRef", valid)
      if (!valid)
        return showValidationErrors(
          "Revisa el formulario, no es válido", index)
    }
  }
  if (only_current){
    save_errors.value = []
    return true
  }
  // console.log("childValidators", childValidators.value)
  if (index === null){
    for (const childValidate of childValidators.value) {
      const isValid = await childValidate()
      if (!isValid) return showValidationErrors(
        "Revisa los elementos dependientes, alguno no es válido")
    }
  }
  else {
    const childValidate = childValidators.value[index]
    // console.log("childValidate at index", index, ":", {
    //   full: childValidate,
    //   name: childValidate?.name || 'anonymous',
    //   length: childValidate?.length,
    //   toString: childValidate?.toString()
    // })
    if (childValidate){
      const isValid = await childValidate()
      if (!isValid) return showValidationErrors(
        "Revisa los elementos dependientes, alguno no es válido", index)
    }
  }
  save_errors.value = []
  return true
}

onMounted(() => {
  if (parentRegister) {
    parentRegister(() => validateAllForms(null, false))
  }
})

onBeforeUnmount(() => {
  if (parentUnregister) {
    parentUnregister(validateAllForms)
  }
})

async function saveItem(item, index) {
  // console.log("saveItem", index, item)
  const is_valid = await validateAllForms(index)
  if (!is_valid) return
  elem_to_save.value = item
  saving.value = true
  index_in_edit.value = index
  save_errors.value = null
  element_errors.value[index] = null
  saveComplex(child_collection.value.snake_name, item)
    .then(() => allFinished(item.pre_data, index))
    .catch(errors => {
      console.error("Errores al guardar:", errors)
      save_errors.value = errors
      saving.value = false
      resetInitialData()
    })
}

async function allFinished(pre_data=null, index=null) {
  if (!elem_to_save.value) {
    console.error("No elem_to_save")
    saving.value = false
    return
  }
  const mixed_res = await saveItemMixed(
    child_collection.value.snake_name, elem_to_save.value, pre_data)
  if (mixed_res.errors){
    if (index !== null)
      element_errors.value[index] = mixed_res.errors
    else
      save_errors.value = [mixed_res.errors]
    saving.value = false
    resetInitialData()
    return
  }
  showSnackbar(`${child_collection.value.name} guardado`)
  saving.value = false
  main_array.value.splice(index_in_edit.value, 1, mixed_res)
  resetInitialData()
}

async function saveNewItem(item, index) {
  const is_valid = await validateAllForms(index, true)
  if (!is_valid) return
  saving.value = true
  saveSimple([props.child_relation_name, item])
    .then(res => {
      // console.log("res", res)
      main_array.value.splice(index, 1, res)
      saving.value = false
      resetInitialData()
    })
    .catch(err => {
      console.error(err)
      save_errors.value = [err.message || 'Error al guardar']
      saving.value = false
    })
}

const final_note_id = computed(() => {
  if (props.note_id)
    return props.note_id
  if (props.main_collection_name === 'mention')
    return props.parent_id
  return null
})

async function acceptItem(pre_item, index) {
  saving.value = true
  index_in_edit.value = index
  const is_valid = await validateAllForms(index, true)
  // console.log("is_valid", is_valid)
  if (!is_valid) {
    saving.value = false
    return
  }
  const params = {...pre_item, ...parent_object.value}
  const child_name = child_collection.value.snake_name
  const new_item = await savePreItem(
    pre_item.path, child_name, final_note_id.value, params)
    showSnackbar(`${child_collection.value.name} aceptado`)
  saving.value = false
  main_array.value.splice(index, 1, new_item)
  resetInitialData()
}

async function discardRecord(pre_item, index) {
  saving.value = true
  index_in_edit.value = index
  const new_pre_item = await discardPreItem(
    pre_item.path, final_note_id.value)
  main_array.value.splice(index, 1)
  main_array.value.push(new_pre_item)
  saving.value = false
  showSnackbar(`${child_collection.value.name} descartado`)
}

const show_all_discarded = ref(false)
const discarded_count = computed(() => {
  if (!main_array.value)
    return 0
  return main_array.value.filter(
    item => item.discarded === true).length
})

const wantDeleteRecord = (item, index) => {
  record_to_delete.value = { item, index, saved: !!item.id }
  save_errors.value = []
  resetDelete()
  dialog_delete.value = true
}

const deleteRecord = async () => {
  const {item, index, saved} = record_to_delete.value
  if (saved && delete_text.value !== 'eliminar')
    return
  if (!item.id) {
    main_array.value.splice(index, 1)
    dialog_delete.value = false
    record_to_delete.value = {}
    return
  }
  const snake = child_collection.value.snake_name
  const action = delete_report_data.value
    ? confirmForceDelete : tryDelete
  const res = await action(snake, item.id)
  if (res.success) {
    main_array.value.splice(index, 1)
    dialog_delete.value = false
    record_to_delete.value = {}
    resetDelete()
  }
}

const total_count = computed(() => {
  try {
    return main_array.value.length
  } catch (e) {
    console.error(e)
    console.log("main_collection_name", props.main_collection_name)
    console.log("filter_group_name", props.filter_group_name)
    console.log("main_array:", main_array.value)
    console.log("parent_id:", props.parent_id)
    // console.log("field:", props.field)
    return 0
  }
})

function resetInitialData(){
  if (selectGroupRef.value){
    selectGroupRef.value.forEach(ref => {
      if (ref && ref.externalSetInitialData)
        ref.externalSetInitialData()
    })
  }
}

const color_child_card = computed(() => {
  return props.second_level ? 'white' : `${props.color}-lighten-5`
})

</script>

<template>
  <v-col :cols="cols" class="py-2 px-2">
    <v-card
      :class="second_level ? 'mt-2' : ''"
      elevation="3"
      variant="elevated"
      :color="`${color}-lighten-${second_level ? 4 : 3}`"
    >
      <ToolbarHeader
        v-if="child_collection"
        :child_collection="child_collection"
        :main_collection_name="main_collection_name"
        :total_count="total_count"
        :filter_group="filter_group"
        :color="`${color}-lighten-${second_level ? 2 : 1}`"
        :second_level="second_level"
        :disabled_buttons="!parent_id"
        :emit_add="emit_add"
        :parent_object="parent_object"
        :additional_fields="additional_fields"
        @unshift-item="main_array.unshift($event)"
        @add-item="emits('add-item', $event)"
      >
        <template #main_buttons>
          <slot name="main_buttons">
          </slot>
        </template>
      </ToolbarHeader>
      <v-card
        v-if="save_errors.length > 0"
        class="ma-2"
        elevation="2"
        color="red-lighten-3"
      >
        Errores: {{save_errors}}
      </v-card>
      <template
        v-for="(item, index) in main_array"
        :key="index"
      >
        <v-card
          v-if="show_all_discarded || (item && item.discarded !== true)"
          class="ma-2"
          elevation="2"
          variant="flat"
          :color="item.discarded ? 'red-lighten-5' : color_child_card"
        >
          <v-card
            v-if="element_errors[index]"
            class="ma-2"
            elevation="2"
            color="red-lighten-3"
          >
            Errores: {{element_errors[index]}}
          </v-card>
          <v-row
            no-gutters
            class="d-flex flex-wrap"
            _class="{'ml-6': second_level && !two_columns}"
          >
            <v-col
              :cols="two_columns ? 6 : 12"
              class="pa-2"
            >
              <v-alert
                v-if="item.path && !parent_id"
                type="warning"
                variant="outlined"
                class="mt-2"
              >
                Para guardar esto, acepta el elemento dependiente
              </v-alert>
              <v-form
                ref="mainForm"
                :class="{'pre_item': item.path && !item.id}"
              >
                <div class="d-flex flex-wrap">
                  <SelectGroup
                    ref="selectGroupRef"
                    v-model="main_array[index]"
                    :filter_group_name="filter_group_name"
                    :main_collection="child_collection"
                    is_toolbar
                    :special_multiple="special_multiple"
                    :forced_level="forced_level"
                    :required="required_full_category"
                  >
                    <template #chip>
                      <slot
                        name="rows_init"
                        :item="item"
                        :index="index"
                      >
                      </slot>
                    </template>
                    <template #actions>
                      <div
                        class="d-flex ga-1"
                        :class="{'flex-column mr-0 ml-2': vertical_actions}"
                      >
                        <v-btn
                          v-if="item.id"
                          @click="wantDeleteRecord(item, index)"
                          icon="delete"
                          color="error"
                          variant="text"
                          class="mt-n2"
                          v-tooltip:top="`Eliminar ${child_collection?.name || 'registro'}`"
                        >
                        </v-btn>
                        <ParagraphFilter
                          v-if="!hide_pre_buttons"
                          :paragraphs="item?.paragraphs"
                          :note_id="note_id"
                          :path="item.path"
                          :class="item.id ? 'mt-n1' : ''"
                        />
                        <v-btn
                          v-if="item.id || item.discarded === undefined"
                          @click="saveItem(item, index)"
                          icon="save"
                          color="success"
                          variant="outlined"
                          :loading="saving && index_in_edit === index"
                          :class="{'mt-n2 ml-2': !vertical_actions}"
                          v-tooltip:top="`Guardar ${child_collection?.name || 'cambios'}`"
                        >
                        </v-btn>
                      </div>
                      <DiscardButtons
                        v-if="!item.id && item.path && !hide_pre_buttons"
                        :discarded="item.discarded"
                        :can_edit_pre_save="!!parent_id"
                        :vertical_actions="vertical_actions"
                        :loading="saving && index_in_edit === index"
                        @discard-record="discardRecord(item, index)"
                        @accept-record="acceptItem(item, index)"
                      />
                    </template>
                  </SelectGroup>
                </div>
                <slot name="rows" :item="item" :index="index">
                </slot>
              </v-form>
<!--              <v-card-actions-->
<!--                class="mt-3"-->
<!--                v-if="partial_save && item.id && false"-->
<!--              >-->
<!--                <v-spacer></v-spacer>-->
<!--                <v-btn-->
<!--                  variant="outlined"-->
<!--                  color="accent"-->
<!--                  :disabled="!item[required_field]"-->
<!--                  :loading="saving"-->
<!--                  @click="saveItem(item, index)"-->
<!--                >-->
<!--                  Guardar {{ child_collection.name }}-->
<!--                </v-btn>-->
<!--                <v-spacer></v-spacer>-->
<!--              </v-card-actions>-->
            </v-col>
            <v-col
              v-if="two_columns"
              cols="6"
              class="my-0"
            >
              <v-card-actions
                v-if="required_field && !item.id && !item.path"
              >
                <v-btn
                  block
                  variant="elevated"
                  color="accent"
                  :disabled="!item[required_field]"
                  :loading="saving"
                  @click="saveNewItem(item, index)"
                >
                  Guardar {{ child_collection.name }}
                </v-btn>
              </v-card-actions>
              <slot
                v-if="item.path || !(required_field && !item.id)"
                name="second-column"
                :item="item"
                :second_index="index"
              >
              </slot>
            </v-col>
          </v-row>
        </v-card>
      </template>
      <v-card
        v-if="discarded_count > 0"
        class="ma-2 px-3 py-1"
        elevation="2"
        color="red-lighten-5"
      >
        <template v-if="!show_all_discarded">

          {{ discarded_count }} {{child_collection.plural_name}} se descartaron
        </template>
        <v-btn
          color="accent"
          variant="outlined"
          size="small"
          @click="show_all_discarded = !show_all_discarded"
          :append-icon="show_all_discarded ? 'keyboard_arrow_up' : 'keyboard_arrow_down' "
        >
          {{ show_all_discarded ? 'Ocultar' : 'Mostrar' }}
          descartados
        </v-btn>
      </v-card>
      <v-alert
        v-if="total_count === 0"
        :type="required ? 'error' : 'warning'"
        variant="flat"
      >
        {{ required ? 'Debes' : 'Intenta' }}
        agregar al menos un {{ child_collection.name }}
      </v-alert>
      <slot name="footer">
      </slot>
    </v-card>
    <DialogDelete
      v-model="dialog_delete"
      v-model:delete_text="delete_text"
      :is_saved="record_to_delete.saved"
      :loading="deleting"
      :report_data="delete_report_data"
      :delete_errors="delete_errors"
      @confirm-delete="deleteRecord"
    />
  </v-col>
</template>

<style scoped>

</style>