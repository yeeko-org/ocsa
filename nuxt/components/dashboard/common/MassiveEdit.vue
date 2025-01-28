<script setup>

import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import {ref} from "vue";
import { saveElement } from "~/composables/save_elements.js";

const props = defineProps({
  full_main: Object,
  collection_data: Object,
  collection_name: String,
  ids_to_edit: Array,
})

const active_fields = ref([])
const saving = ref(false)
const emits = defineEmits(['massive-finish'])

const final_collection_data = computed(() => {
  if (props.collection_data)
    return props.collection_data
  return schemas.value.collections_dict[props.collection_name]
})

const visible_filters = computed(() => {
  console.log("collection_data", final_collection_data.value)
  console.log("filters", final_collection_data.value.collection_filters)
  return final_collection_data.value.collection_filters.filter(
    coll => active_fields.value.includes(coll.name))
  // let collection_filters =
  // if (!final_collection_data.value)
  //   return []
  // return final_collection_data.value.filters_list.filter(
  //   filter_box => filter_box.visible)
})

const merged_params = computed(() => {
  let params = {}
  const all_levels = [
      'category_group',
      'category_type',
      'category_subtype',
  ]
  visible_filters.value.forEach(filter_box => {
    const models = all_levels.reduce((acc, level) => {
      if (filter_box[level])
        acc.push(filter_box[level])
      return acc
    }, [])
    console.log("models", models)
    final_collection_data.value.fields.forEach(field => {
      if (!field.related_snake_name || field.relation_type === 'one_to_many')
        return
      if (models.includes(field.related_snake_name))
        params[field.name] = props.full_main[field.name]
    })
  })
  console.log("params", params)
  return params
})

function sendMassiveEdit() {
  saving.value = true
  // console.log("merged_params", merged_params.value)
  const final_params = {...merged_params.value, elems_ids: props.ids_to_edit}
  saveElement(final_collection_data.value, final_params).then((res) => {
    console.log("res", res)
    saving.value = false
    active_fields.value = []
    emits('massive-finish')
  })
}

</script>

<template>
  <v-card class="mb-3 pa-3" elevation="8">
    <span
      class="mr-2 text-subtitle-1"
    >Selecciona los campos a editar masivamente:</span>
    <v-code>
      {{merged_params}}
    </v-code>
    <v-chip-group
      v-model="active_fields"
      class="mr-2"
      multiple
      color="accent"
      direction="vertical"
    >
      <div
        v-for="field in final_collection_data.collection_filters"
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
            :final_filters="full_main"
            :collection="field.key_name"
            collection_group="status"
            clearable
            hide-details
            style="max-width: 320px; min-width: 200px;"
            @change-status="applyFilters"
            is_filter
            class="pr-3 pl-0 py-1"
          />
          <div
            v-else-if="field.key_name"
            class="pr-3 pl-0 py-1 d-flex"
          >
            <SelectGroup
              :filter_group_name="field.key_name"
              :main_object="full_main"
              :category_group_value="field.category_group_value"
              :forced_level="field.forced_level || 'other'"
            />
          </div>
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