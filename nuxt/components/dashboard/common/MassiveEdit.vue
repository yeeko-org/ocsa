<script setup>

import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import { saveElement } from "~/composables/save_elements.js";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from 'pinia'
import SelectSubtype from "~/components/dashboard/common/select/SelectSubtype.vue";
import CardCommon from "~/components/dashboard/common/generic/CardCommon.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  collection_data: Object,
  collection_name: String,
  ids_to_edit: Array,
})
const full_main = defineModel({type: Object, required: true})

const active_fields = ref([])
const saving = ref(false)
const emits = defineEmits(['massive-finish'])

const final_collection_data = computed(() => {
  if (props.collection_data)
    return props.collection_data
  return schemas.value.collections_dict[props.collection_name]
})

const visible_filters = computed(() => {
  return final_collection_data.value.collection_filters.filter(
    coll => active_fields.value.includes(coll.name))
})

const extra_fields = computed(() => {
  return final_collection_data.value.extra_massive_edit_fields || []
})

const available_fields = computed(() => {
  const coll = final_collection_data.value
  let massive_fields = coll.collection_filters.filter(f=>
      !f.is_custom && f.can_massive_edit !== false)
  // coll.extra_massive_edit_fields || []
  // const extra_fields = coll.extra_massive_edit_fields || []
  extra_fields.value.forEach(ef => {
    const full_field = coll.fields.find(f => f.name === ef)
    if (full_field)
      massive_fields.push(full_field)
  })
  return massive_fields
})

const merged_params = computed(() => {
  let params = {}
  const all_levels = [
      'category_group',
      'category_type',
      'category_subtype',
  ]
  visible_filters.value.forEach(filter_box => {
    let models = all_levels.reduce((acc, level) => {
      if (filter_box[level])
        acc.push(filter_box[level])
      return acc
    }, [])
    final_collection_data.value.fields.forEach(field => {
      if (!field.related_snake_name || field.relation_type === 'one_to_many')
        return
      if (models.includes(field.related_snake_name))
        params[field.name] = full_main.value[field.name]
    })
  })
  active_fields.value.forEach(field_name => {
    if (extra_fields.value.includes(field_name))
      params[field_name] = full_main.value[field_name] || null
  })
  visible_filters.value.forEach(filter_box => {
    if (filter_box.collection)
      params[filter_box.collection] = full_main.value[filter_box.collection]
  })

  return params
})

const full_related = ref({})

function selectItem(field, item) {
  // console.log("selectItem", field, item)
  full_main.value[field.name] = item.id
  full_related.value[field.name] = item
}

function sendMassiveEdit() {
  saving.value = true
  const final_params = {...merged_params.value, elems_ids: props.ids_to_edit}
  // console.log("final_params", final_params)
  saveElement(final_collection_data.value, final_params).then((res) => {
    // console.log("res", res)
    saving.value = false
    active_fields.value = []
    emits('massive-finish')
  })
}

</script>

<template>
  <v-card class="mb-3 pa-3" elevation="5">
    <span
      class="mr-2 text-title-medium"
    >Selecciona los campos a editar masivamente:</span>
    <v-chip-group
      v-model="active_fields"
      class="mr-2"
      multiple
      color="accent"
      direction="vertical"
    >
      <div
        v-for="field in available_fields"
        :key="field.name"
        class="d-flex align-center mt-2"
      >
        <div style="width: 300px">
          <v-chip
            :value="field.name"
            filter
            variant="tonal"
            width="300"
            class="mb-4"

          >
            {{ field.name }}
          </v-chip>
        </div>
        <template
          v-if="active_fields.includes(field.name)"
        >
          <StatusDetail
            v-if="field.collection"
            v-model="full_main"
            :collection="field.key_name"
            clearable
            hide-details
            style="max-width: 320px; min-width: 200px;"
            @change-status="applyFilters"
            class="pr-3 pl-0 py-1"
          />
          <div
            v-else-if="field.key_name"
            class="pr-3 pl-0 py-1 d-flex"
          >
            <SelectGroup
              v-if="field.category_type"
              v-model="full_main"
              :filter_group_name="field.key_name"
              :category_group_value="field.category_group_value"
              :forced_level="field.forced_level || 'other'"
            />
            <SelectSubtype
              v-else
              v-model="full_main"
              :filter_collection_name="field.category_subtype"
              :main_collection="final_collection_data"
            />
          </div>
          <CardCommon
            v-else-if="field.related_snake_name"
            :collection_name="field.related_snake_name"
            :full_main="full_related[field.name]"
            class="my-2"
            indirect_get
            @selected-item="selectItem(field, $event)"
          />
          <h5 v-else>{{field.title || field.name}}</h5>
        </template>
      </div>
    </v-chip-group>
    <v-card-actions>
      <v-btn
        color="accent"
        variant="elevated"
        :loading="saving"
        @click="sendMassiveEdit"
      >
        Guardar cambios
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>

</style>