<script setup>

import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

import {computed} from "vue";
import {useMainStore} from "~/store/index.js"
import {storeToRefs} from "pinia"

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  main_array: Array,
  filter_group_name: String,
  child_field: String,
})

const filter_node = computed(() => all_nodes.value[props.filter_group_name])

const all_counts = computed(() => {
  const category_type = filter_node.value.data.category_type
  let types_counts = props.main_array.reduce((acc, mention) => {
    mention[props.child_field].forEach(elem => {
      if (acc[elem[category_type]])
        acc[elem[category_type]] += 1
      else
        acc[elem[category_type]] = 1
    })
    return acc
  }, {})

  let groups_counts = filter_node.value.children.reduce((acc, group) => {
    const data = group.data
    let new_value = {...data, current_types: [], complement: []}
    return {...acc, [data.id]: new_value}
  }, {})

  Object.entries(types_counts).forEach(([key, value]) => {
    const type_node = filter_node.value.find(
      type => type.id === `type_${key}`)
    const current_group = type_node.data[filter_node.value.data.category_group]
    groups_counts[current_group].current_types.push({
      name: type_node.data.name,
      count: value
    })
    groups_counts[current_group].complement.push(
        `-${type_node.data.name} (${value})`)
  })
  return groups_counts

})

</script>

<template>
  <HeaderChip
    v-for="group in Object.values(all_counts)"
    :count="group.current_types.length"
    :icon="group.icon"
    :label="`Afectación ${group.name}`"
    :label_plural="`Afectaciones ${group.name}es`"
    :color="group.color"
    :tooltip_complement="group.complement.join('<br>')"
    class="mr-1"
  />
</template>

<style scoped>

</style>