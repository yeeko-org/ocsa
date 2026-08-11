<script setup>
import {useMainStore} from "~/store/index.js";

const mainStore = useMainStore()
const { criteria } = mainStore

const props = defineProps({
  main: Object,
  is_simple: Boolean,
  direct_criteria: Array,
  indirect_criteria: Object,
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

const emits = defineEmits(['add-field'])

const criteria_data = computed(() => {
  if (props.direct_criteria)
    return props.direct_criteria
  const criteria_values = props.main?.criteria || props.indirect_criteria || {}
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
    let base_criteria = {
      count: "Sin",
      value: "identificado en el texto",
      is_selected: true,
    }
    const negative_fields = [
      {
        "key": "is_foreign",
        "name": 'Es una nota extranjera',
        "icon": 'public',
      },
      {
        "key": "is_political_opinion",
        "name": 'Contiene opinión política',
        "icon": 'announcement',
        "color": 'purple-darken-3',
      },
      {
        "key": "is_public_policy",
        "name": "Es una política pública",
        "icon": 'gavel',
      },
      {
        "key": "is_political_opinion",
        "name": "Es artículo de opinión / política",
        "icon": 'how_to_vote',
      },
      {
        "key": "is_labor_conflict_only",
        "name": "Sólo trata conflicto laboral",
        "icon": 'work',
      },
      {
        "is_inverse": true,
        "key": "is_specific_project",
        "name": "El proyecto no es específico",
        "icon": 'factory',
      },
      {
        "is_inverse": true,
        "key": "is_extractivist_or_big_scale",
        "name": "No es extractivista o de gran escala",
        "icon": 'handyman',
      },
    ]
    negative_fields.forEach((neg_field) => {
      if (!neg_field.is_inverse && !criteria_values[neg_field.key])
        return
      if (neg_field.is_inverse){
        if (!criteria_values.hasOwnProperty(neg_field.key))
          return
        else if (criteria_values[neg_field.key])
          return
      }
      const color = neg_field.color || 'red-darken-3'
      criteria_items.push({
        ...base_criteria,
        ...neg_field,
        public_name: neg_field.name,
        color: color,
        final_color: color,
      })
    })
  }
  return criteria_items
})

const total_count = computed(() => {
  return criteria_data.value.reduce((acc, field) => acc + field.count, 0)
})

// function addField(field) {
//   // console.log('addField', field)
//   if (props.selected_fields.includes(field)){
//     const index = props.selected_fields.indexOf(field)
//     props.selected_fields.splice(index, 1)
//   }
//   else
//     props.selected_fields.push(field)
//   emits('reset-filters')
// }

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
        @click="emits('add-field', field.name)"
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
            class="text-title-medium"
          >
            {{ field.name }}
          </v-card-title>
          <v-card-text v-if="field.count">
            {{field.count}} párrafos: {{field.value}}
          </v-card-text>
        </v-card>
      </v-tooltip>
    </div>

  </v-card>
</template>

<style scoped>

</style>