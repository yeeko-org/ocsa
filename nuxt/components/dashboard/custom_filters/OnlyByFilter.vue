<script setup>
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import DescriptionIcon from "~/components/dashboard/common/utils/DescriptionIcon.vue";
const mainStore = useMainStore()
const { collections_summary } = storeToRefs(mainStore)

const props = defineProps({
  final_filters: Object,
  field: String,
  label: {
    type: String,
    default: "Usuario",
  },
  filter_box: Object,
})

const items = computed(() => {
  if (!props.filter_box)
    return []
  // console.log("collections_summary", collections_summary.value)
  if (props.filter_box.custom_options){
    return props.filter_box.custom_options
  }
  const options = props.filter_box.options || []
  return options.map((opt) => {
    return collections_summary.value[opt]
  })
})

const has_descriptions = computed(() =>
  items.value.some(item => item?.description))

// El menú hereda el ancho del select (máx. 220), demasiado angosto para
// leer las descripciones.
const menu_props = computed(() =>
  has_descriptions.value ? {width: 340} : undefined)

</script>

<template>
  <v-select
    v-model="final_filters[field]"
    :items="items"
    :label="label"
    item-title="plural_name"
    item-value="value"
    clearable
    variant="underlined"
    density="compact"
    hide-details
    min-width="140"
    max-width="220"
    :menu-props="menu_props"
  >
    <template #item="{ props: item_props, item }">
      <v-list-item
        v-bind="item_props"
        :subtitle="item.raw?.description"
      />
    </template>
    <template
      v-if="filter_box?.description"
      #append
    >
      <DescriptionIcon
        :description="filter_box.description"
        icon_size="small"
      />
    </template>
  </v-select>
</template>

<style scoped>

</style>
