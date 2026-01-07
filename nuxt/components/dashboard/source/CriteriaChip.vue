<script setup>
import {useMainStore} from "~/store/index.js";

const mainStore = useMainStore()
const { criteria } = mainStore

const props = defineProps({
  main: Object,
  is_simple: Boolean,
  direct_criteria: Array,
  is_filter: Boolean,
  selected_fields: {
    type: Array,
    required: false,
  },
  show_negatives: Boolean,
})

// opponents: list[int] = []
// social_impacts: list[int] = []
// ecological_impacts: list[int] = []
// acts_of_violence: list[int] = []
// collective_actions: list[int] = []
// is_foreign: bool | None = None
const fields = [
  'opponents',
  'social_impacts',
  'ecological_impacts',
  'acts_of_violence',
  'collective_actions',
]

// const selected_fields = ref([])
const emits = defineEmits(['update:selected_fields', 'reset-filters'])

const criteria_data = computed(() => {
  if (props.direct_criteria)
    return props.direct_criteria
  const criteria_values = props.main.criteria || []
  let criteria_items = fields.map((field) => {
    const criteria_data = criteria[field] || {}
    const is_selected = props.is_filter
      ? props.selected_fields.includes(criteria_data.name)
      : false
    const count = criteria_values[field]?.length || 0
    let final_color = null
    if (!count)
      final_color = 'grey-lighten-1'
    else if (props.is_filter && is_selected)
      final_color = 'white'
    else
      final_color = criteria_data.color
    return {
      ...criteria_data,
      "count": count,
      "value": criteria_values[field] || [],
      "key": field,
      "final_color": final_color,
      "is_selected": is_selected,
    }
  })
  if (props.show_negatives){
    if (criteria_values.is_foreign){
      criteria_items.push({
        name: 'Es una pre-nota extranjera',
        public_name: 'Es una nota extranjera',
        icon: 'public',
        color: 'red-darken-3',
        final_color: 'red-darken-3',
        count: "Sin",
        value: "identificado en el texto",
        key: 'is_foreign',
        is_selected: true,
      })
    }
    if (criteria_values.is_political_opinion) {
      criteria_items.push({
        name: 'Contiene opinión política',
        public_name: 'Contiene opinión política',
        icon: 'announcement',
        color: 'purple-darken-3',
        final_color: 'purple-darken-3',
        count: "Sin",
        value: "identificado en el texto",
        key: 'is_political_opinion',
        is_selected: true,
      })
    }
  }
  return criteria_items
})

const total_count = computed(() => {
  return criteria_data.value.reduce((acc, field) => acc + field.count, 0)
})

function addField(field) {
  // console.log('addField', field)
  if (props.selected_fields.includes(field)){
    const index = props.selected_fields.indexOf(field)
    props.selected_fields.splice(index, 1)
  }
  else
    props.selected_fields.push(field)
  emits('reset-filters')
}

</script>

<template>
  <v-card
    rounded
    :variant="is_simple ? 'flat' : total_count ? 'outlined' : 'tonal'"
    :color="is_simple ? 'transparent' : total_count ? 'blue' : 'warning'"
    class="d-flex"
    :class="is_simple ? 'pa-0' : 'pa-2'"
  >
    <div
      v-for="field in criteria_data"
      :key="field.name"
      class="d-flex flex-column align-center"
      :class="is_simple ? 'pl-0 pr-1' : 'px-1'"
    >
      <v-btn
        v-if="is_filter"
        icon
        size="small"
        :color="field.count ? field.color : 'grey-ligthen-2'"
        :variant="field.is_selected ? 'elevated' : 'plain'"
        @click="addField(field.name)"
        :disabled="!field.count"
      >
        <v-icon
          :color="field.final_color"
        >
          {{ field.icon }}
        </v-icon>
      </v-btn>
      <v-icon
        v-else
        :color="field.count ? field.color : 'grey-lighten-2'"
        :size="is_simple ? 18 : 24"
      >
        {{ field.icon }}
      </v-icon>
      <v-tooltip
        activator="parent"
        location="bottom"
      >
        <v-card
          :color="field.count ? field.color : 'grey-lighten-2'"
          class="mx-n4 my-n2"
        >
          <v-card-title
            class="text-subtitle-1"
          >
            {{ field.name }}
          </v-card-title>
          <v-card-text v-if="!is_simple">
            {{field.count}} párrafos: {{field.value}}
          </v-card-text>
        </v-card>
      </v-tooltip>
    </div>

  </v-card>
</template>

<style scoped>

</style>