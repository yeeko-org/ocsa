<script setup>

import HeaderChip from "~/components/dashboard/common/utils/HeaderChip.vue";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { cats, event_types_dict } = mainStore

const props = defineProps({
  mentions: {
    type: Array,
    required: true,
  },
})

const events_count = computed(() => {
  const all_events = props.mentions.reduce((acc, mention) => {
    const hydrated_events = mention.events.map(event => {
      event.event_group = event_types_dict[event.event_type]
      return event
    })
    return acc.concat(hydrated_events)
  }, [])
  const counts_by_group = cats.event_group.reduce((list, group) => {
    if (!group.is_conflict_related){
      cats.purpose.forEach(purpose => {
        const purpose_events = all_events.filter(
          event => event.purpose === purpose.id && event.event_group === group.id)

        if (purpose_events.length > 0) {
          list.push({
            ...group,
            name: `${group.name} - ${purpose.name}`,
            // xcolor: group.color,
            color: `${purpose.color}-lighten-3`,
            is_purpose: true,
            // color: purpose.color,
            // color: 'deep-orange-lighten-3',
            count: purpose_events.length,
          })
        }
      })
      // let new_group = {...group, purposes: []}
      return list
    }
    const group_events = all_events.filter(event => event.event_group === group.id)
    list.push({
      ...group,
      count: group_events.length,
    })
    return list
  }, [])
  // console.log("counts_by_group", counts_by_group)
  return counts_by_group
})

</script>

<template>
  <v-card
    color="lime"
    class="d-flex xpa-1 ga-1"
    rounded="lg"
    bg-color="lime"
    variant="outlined"
    style="border-width: 2px; padding: 3px;"
  >
    <HeaderChip
      v-for="event in events_count"
      :key="event.id"
      :count="event.count"
      :icon="event.icon"
      :label="event.name"
      :label_plural="event.name + 's'"
      :color="event.color"
      inside_group
      :is_purpose="event.is_purpose"
    />
  </v-card>
</template>

<style scoped>

</style>