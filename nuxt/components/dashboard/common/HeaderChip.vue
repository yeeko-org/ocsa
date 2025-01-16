<script setup>

import { computed } from 'vue'
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  count: Number,
  collection_name: String,
  icon: String,
  label: String,
  label_plural: String,
  color: String,
  tooltip_complement: String,
  is_simple: Boolean,
  horizontal: Boolean,
})

const collection_data = computed(() => {
  if (!props.collection_name)
    return {}
  return schemas.value.collections_dict[props.collection_name]
})

const final_label = computed(() => {
  return props.count === 1
    ? (props.label || collection_data.value.name || 'elemento')
    : (props.label_plural || collection_data.value.plural_name || 'elementos')
})

const final_color = computed(() => {
  return props.color || collection_data.value.color
})

const final_icon = computed(() => {
  return props.icon || collection_data.value.icon || 'dashboard'
})

</script>

<template>
  <v-card
    variant="tonal"
    :color="final_color"
    class="text-body-2 px-2"
    :class="horizontal ? 'py-2' : 'py-1'"
  >
    <div
      class="d-flex align-center justify-center"
      :class="horizontal ? 'flex-row' : 'flex-column'"
    >
      <div class="px-1">
        <v-icon
          v-if="!count"
          size="18"
          color="warning"
        >
          warning_amber
        </v-icon>
        <div
          v-else
        >
          {{count}}
          <span v-if="is_simple">
            /&nbsp;∞
          </span>
        </div>
      </div>
      <v-icon
        :size="horizontal ? 18 : 20"
        :color="final_color"
        :class="{ 'mt-1': !horizontal }"
      >
        {{ final_icon }}
      </v-icon>
    </div>
    <v-tooltip
      activator="parent"
      location="top"
      :bg-color="final_color"
      :color="final_color"
      _style="`background-color: ${color};`"
    >
      <div class="font-weight-bold">
        {{count}} {{ final_label }}
        <span v-if="is_simple">
          con relación <br>
        </span>
        <span v-if="is_simple" class="text-caption text-warning">
          (El total real puede ser mayor)
        </span>
      </div>
      <!--style with break-word-->
      <div
        v-if="tooltip_complement"
        v-html="tooltip_complement"
        style="max-width: 500px; word-wrap: break-word;"
      ></div>

    </v-tooltip>
  </v-card>

</template>

<style scoped>

</style>