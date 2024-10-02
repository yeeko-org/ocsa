<script setup>

import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

import {computed} from "vue";
import {useMainStore} from "~/store/index.js"
import {storeToRefs} from "pinia"

const mainStore = useMainStore()
const { cats, impact_groups } = storeToRefs(mainStore)

const props = defineProps({
  mentions: Array,
})

const impact_counts = computed(() => {
  let impacts = props.mentions.reduce((acc, mention) => {
    mention.impacts.forEach(impact => {
      if (acc[impact.impact_type])
        acc[impact.impact_type] += 1
      else
        acc[impact.impact_type] = 1
    })
    return acc
  }, {})
  let impact_groups_new = Object.keys(impact_groups.value).reduce((acc, group) =>
    ({...acc, [group]: {"impact_types": [], "complement": []}}), {})
  Object.entries(impacts).forEach(([key, value]) => {
    const impact_type = cats.value.impact_types.find(
        impact => impact.id === Number(key))
    const group = impact_type.is_social ? 'social' : 'environmental'
    const new_value = {name: impact_type.name, count: value}
    impact_groups_new[group]["impact_types"].push(new_value)
    impact_groups_new[group]["complement"].push(`-${impact_type.name} (${value})`)
  })
  return impact_groups_new
})

</script>

<template>
  <HeaderChip
    :count="impact_counts.social.impact_types.length"
    icon="groups"
    label="afectación social"
    label_plural="afectaciones sociales"
    color="teal"
    :tooltip_complement="impact_counts.social.complement.join('<br>')"
    class="mx-1"
  />
  <HeaderChip
    :count="impact_counts.environmental.impact_types.length"
    icon="eco"
    label="afectación ambiental"
    label_plural="afectaciones ambientales"
    color="green"
    :tooltip_complement="impact_counts.environmental.complement.join('<br>')"
    class="mr-2"
  />

</template>

<style scoped>

</style>