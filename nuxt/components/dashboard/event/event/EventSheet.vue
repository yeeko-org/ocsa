<script setup>

import ImpactSheet from "~/components/dashboard/impact/impact/ImpactSheet.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import EventToolbar from "~/components/dashboard/source/EventToolbar.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
  collection_data: Object,
})

const mention = computed(() => {
  if (!props.full_main.involvements)
    return []
  const participants = props.full_main.involvements.map(involvement => {
    return involvement.participant_full
  })
  console.log("participants", participants)
  return {"events": [props.full_main], participants: participants}
})

</script>

<template>

  <v-card class="mb-4 pa-3">
    <EventToolbar
      :mention="mention"
    />
<!--    <ToolbarCommon-->
<!--      :main_object="full_main"-->
<!--      main_collection_name="event"-->
<!--      filter_group_name="involved_roles"-->
<!--      child_relation_name="involved"-->
<!--      field="involvements"-->
<!--      color="blue"-->
<!--      required-->
<!--    >-->
<!--      <template #rows="{ item }">-->
<!--        <v-card variant="tonal" color="blue" class="pa-3 mb-3">-->
<!--          {{ item.participant.actor_full.name }}-->
<!--        </v-card>-->
<!--        <div class="text-subtitle-1">Número de víctimas:</div>-->
<!--        <div class="d-flex mr-8">-->
<!--          <v-text-field-->
<!--            v-model="item.number_women"-->
<!--            type="number"-->
<!--            label="Mujeres"-->
<!--            class="mr-2"-->
<!--            variant="outlined"-->
<!--            density="compact"-->
<!--            max-width="140"-->
<!--            hide-details-->
<!--          ></v-text-field>-->
<!--          <v-text-field-->
<!--            v-model="item.number_men"-->
<!--            type="number"-->
<!--            label="Hombres"-->
<!--            class="mr-2"-->
<!--            variant="outlined"-->
<!--            density="compact"-->
<!--            max-width="140"-->
<!--            hide-details-->
<!--          ></v-text-field>-->
<!--          <v-text-field-->
<!--            v-model="item.number_mix"-->
<!--            type="number"-->
<!--            label="Otros"-->
<!--            class="mr-2"-->
<!--            variant="outlined"-->
<!--            density="compact"-->
<!--            max-width="140"-->
<!--            hide-details-->
<!--          ></v-text-field>-->
<!--        </div>-->
<!--      </template>-->
<!--    </ToolbarCommon>-->
<!--    <LocationsToolbar-->
<!--      v-if="full_main"-->
<!--      :full_main="full_main"-->
<!--      main_collection_name="event"-->
<!--      second_level-->
<!--    />-->

  </v-card>
  <ImpactSheet
    :full_main="full_main"
  />
</template>

<style scoped>

</style>