<script setup>
import {useMainStore} from "~/store/index.js";

const mainStore = useMainStore()
const { criteria } = mainStore

const props = defineProps({
  main: Object,
  is_simple: Boolean,
  direct_criteria: Array,
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


const criteria_data = computed(() => {
  if (props.direct_criteria) {
    return props.direct_criteria
  }
  const criteria_values = props.main.criteria || []
  return fields.map((field) => {
    return {
      ...criteria[field],
      "count": criteria_values[field]?.length || 0,
      "value": criteria_values[field] || [],
    }
  })
})

const total_count = computed(() => {
  return criteria_data.value.reduce((acc, field) => acc + field.count, 0)
})


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
      <v-icon
        :color="field.count ? field.color : 'grey-lighten-2'"
        :size="is_simple ? 18 : 24"
      >
        {{ field.icon }}
      </v-icon>
      <span
        v-if="false"
        class="text-caption"
        :class="`text-${field.count ? field.color: 'grey-lighten-2'}`"
      >
        {{ field.count }}
      </span>
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
            _class="`text-${position.color}`"
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