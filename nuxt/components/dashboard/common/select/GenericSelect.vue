<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import { VSelect, VAutocomplete } from "vuetify/components"
import {useRules} from "~/composables/useRules.js";
const { rules } = useRules()

const props = defineProps({
  level_name: String,
  collection_data: Object,

  is_filter: Boolean,
  filter_null: Boolean,
  filter_multiple: Boolean,

  main_width: Number,
  item_value: {
    type: String,
    default: 'id',
  },
  item_title: {
    type: String,
    default: 'name',
  },
  items: {
    type: Array,
    required: true,
  },
  is_multiple: Boolean,
  required: Boolean,
  forced_clearable: Boolean,
  is_autocomplete: Boolean,
})
const main_object = defineModel({type: Object, required: true})
const emits = defineEmits(['open-dialog', 'update-value'])

const searchQuery = ref('')

const customFilter = (value, query, item) => {
  if (!query) return true

  const searchText = query.toLowerCase()
  const name = (item.raw[props.item_title] || '').toLowerCase()
  const description = (item.raw.description || '').toLowerCase()

  return name.includes(searchText) || description.includes(searchText)
}

// Sort items: name matches first, then description matches
const sortedItems = computed(() => {
  if (!searchQuery.value || !props.is_autocomplete) {
    return props.items
  }

  const query = searchQuery.value.toLowerCase()

  return [...props.items].sort((a, b) => {
    const aName = (a[props.item_title] || '').toLowerCase()
    const bName = (b[props.item_title] || '').toLowerCase()
    const aDesc = (a.description || '').toLowerCase()
    const bDesc = (b.description || '').toLowerCase()

    const aMatchesName = aName.includes(query)
    const bMatchesName = bName.includes(query)

    // Both match in name - keep order
    if (aMatchesName && bMatchesName) return 0

    // Only one matches in name - prioritize it
    if (aMatchesName) return -1
    if (bMatchesName) return 1

    // Neither matches in name, check description
    const aMatchesDesc = aDesc.includes(query)
    const bMatchesDesc = bDesc.includes(query)

    if (aMatchesDesc && !bMatchesDesc) return -1
    if (!aMatchesDesc && bMatchesDesc) return 1

    return 0
  })
})

const show_add = computed(() => {
  if (!props.collection_data)
    return false
  return props.collection_data.open_insertion
})

const final_rules = computed(() => {
  const calc_rules = []
  // has_content: value => (value && value.length > 0) || "Debes seleccionar al menos una opción",
  // has_content: (value) => {
  //   if (Array.isArray(value)) {
  //     return value.length > 0 || "Debes seleccionar al menos una opción"
  //   }
  //   return !!value || "Debes seleccionar al menos una opción"
  // },
  if (props.required){
    if (props.is_multiple)
      calc_rules.push(rules.some_in_array)
    else
      calc_rules.push(rules.required)
  }
  // console.log("rules", rules)
  // if (props.collection_data.snake_name === 'interest_subtype'){
  //   console.log("props.collection_data.name", props.collection_data.snake_name)
  //   console.log("calc_rules", calc_rules)
  // }
  return calc_rules
})

const selectComponent = computed(() => {
  return props.is_autocomplete ? VAutocomplete : VSelect
})

function changeValue(val){
  // console.log('changeValue', val)
  // console.log('collection_data', props.collection_data)
  main_object.value[`${props.level_name}_null`] = null
  emits('update-value', val)
}

function sendNull(){
  main_object.value[props.level_name] = null
  main_object.value[`${props.level_name}_null`] = true
}

function openDialog(is_add=true){
  emits('open-dialog', is_add)
}

</script>

<template>
  <component
    :is="selectComponent"
    v-model="main_object[level_name]"
    :items="sortedItems"
    :item-title="item_title"
    :item-value="item_value"
    :custom-filter="customFilter"
    :variant="is_filter ? 'underlined' : 'outlined'"
    :clearable="is_filter || forced_clearable"
    :hide-details="is_filter"
    :density="is_filter ? 'compact' : 'default'"
    :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
    :multiple="is_multiple || filter_multiple"
    :rules="final_rules"
    @update:model-value="changeValue"
    @update:search="searchQuery = $event"
  >
    <template #append-item v-if="!is_filter">
      <div class="px-2 d-flex align-center">
        <template v-if="show_add">
          <div
            class="flex-grow-1 pr-2"
          >
            <v-btn
              variant="elevated"
              color="accent"
              append-icon="add"
              block
              @click="openDialog(true)"
            >
              Agregar
            </v-btn>
          </div>
          <div class="flex-shrink-1">
            <v-btn
              variant="outlined"
              color="accent"
              icon
              @click="openDialog(false)"
              v-tooltip="`Gestionar ${collection_data.plural_name}`"
            >
              <v-icon>settings</v-icon>
            </v-btn>
          </div>
        </template>
        <v-btn
          v-else
          variant="outlined"
          color="accent"
          class="mt-2 _mb-1"
          append-icon="settings"
          block
          @click="openDialog(false)"
        >
          Gestionar
        </v-btn>
      </div>
    </template>
    <template #append-item v-if="filter_null">
      <v-list-item
        title="Filtrar vacíos"
        @click="sendNull"
      >
        <template v-slot:prepend>
          <v-icon
            class="mr-n3"
            :color="'grey'"
            :icon="'circle'"
          ></v-icon>
        </template>
      </v-list-item>
    </template>
    <template #item="{ item, props: {onClick, title, value} }">
      <v-list-item
        @click="onClick"
        :title="title"
        _subtitle="item.raw.description"
        :value="value"
        :lines="false"
        max-width="400"
        min-height="52"
        :disabled="['expired', 'rejected'].includes(item.raw.status_validation)"
      >
        <template v-slot:prepend v-if="item.raw.icon">
          <v-icon
            :color="item.raw.color || 'grey-darken-3'"
            :icon="item.raw.icon || 'trip_origin'"
          ></v-icon>
        </template>
        <template
          v-slot:title
          v-if="item.raw.status_validation !== undefined"
        >
          <div class="d-flex align-start">
            {{ item.title }}
            <StatusChip
              collection="validation"
              :main="item.raw"
              x_small
              disabled
              hide_details
            />
          </div>
        </template>
        <template
          v-slot:subtitle
          v-if="item.raw.description"
        >
          <div class="d-flex align-start">
            {{ item.raw.description.substring(0, 120) }}{{ item.raw.description.length > 120 ? '...' : '' }}
            <v-tooltip
              v-if="item.raw.description"
              activator="parent"
              :open-on-hover="true"
              :close-delay="0"
              :open-delay="0"
              location="right"
              :max-width="400"
            >
              {{ item.raw.description }}
            </v-tooltip>

          </div>

        </template>

      </v-list-item>
    </template>
    <template #selection="{ item }" v-if="!is_multiple">
      <v-icon
        v-if="item.raw.icon"
        :color="item.raw.color || 'grey-darken-3'"
        :icon="item.raw.icon || 'trip_origin'"
        class="mr-2"
      ></v-icon>
      {{ item.title }}
      <StatusChip
        v-if="item.raw.status_validation !== undefined"
        collection="validation"
        :main="item.raw"
        x_small
        disabled
        hide_details
      />
    </template>
  </component>
</template>

<style scoped>

</style>