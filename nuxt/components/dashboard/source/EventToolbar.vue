<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import {computed} from "vue";
const mainStore = useMainStore()
const { event_group_violence } = storeToRefs(mainStore)


const props = defineProps({
  mention: Object,
})

const all_actors = computed(() => {
  return props.mention.participants.map(participant => {
    return {...participant.actor_full, ...participant}
  })
})

</script>

<template>
  <ToolbarCommon
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="event_types"
    child_relation_name="event"
    field="events"
    two_columns
    color="lime"
    :additional_fields="{'involvements': [], 'locations': []}"
    required
  >
    <template #rows="{ item }">
      <v-textarea
        v-model="item.description"
        label="Descripción del evento (opcional)"
        variant="outlined"
        density="compact"
        rows="1"
        hide-details
        auto-grow
        style="width: 100%; max-width: 600px;"
      >
      </v-textarea>
      <template v-if="item.event_group === event_group_violence.id">
        <div class="text-subtitle-1 mt-4">Número de víctimas:</div>
        <div class="d-flex mr-8">
          <v-text-field
            v-model="item.number_women"
            type="number"
            label="Mujeres"
            class="mr-2"
            variant="outlined"
            density="compact"
            max-width="140"
            hide-details
          ></v-text-field>
          <v-text-field
            v-model="item.number_men"
            type="number"
            label="Hombres"
            class="mr-2"
            variant="outlined"
            density="compact"
            max-width="140"
            hide-details
          ></v-text-field>
          <v-text-field
            v-model="item.number_mix"
            type="number"
            label="Otros"
            class="mr-2"
            variant="outlined"
            density="compact"
            max-width="140"
            hide-details
          ></v-text-field>
        </div>
      </template>
    </template>
    <template #second-column="{ item }">
      <ToolbarCommon
        :main_object="item"
        main_collection_name="event"
        filter_group_name="involved_roles"
        child_relation_name="involved"
        field="involvements"
        second_level
        color="blue"
        required
      >
        <template #rdows="{ item }">
          <v-select
            v-model="item.participant"
            :items="all_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
          ></v-select>
<!--          <div class="text-subtitle-1">Número de víctimas:</div>-->
<!--          <div class="d-flex mr-8">-->
<!--            <v-text-field-->
<!--              v-model="item.number_women"-->
<!--              type="number"-->
<!--              label="Mujeres"-->
<!--              class="mr-2"-->
<!--              variant="outlined"-->
<!--              density="compact"-->
<!--              max-width="140"-->
<!--              hide-details-->
<!--            ></v-text-field>-->
<!--            <v-text-field-->
<!--              v-model="item.number_men"-->
<!--              type="number"-->
<!--              label="Hombres"-->
<!--              class="mr-2"-->
<!--              variant="outlined"-->
<!--              density="compact"-->
<!--              max-width="140"-->
<!--              hide-details-->
<!--            ></v-text-field>-->
<!--            <v-text-field-->
<!--              v-model="item.number_mix"-->
<!--              type="number"-->
<!--              label="Otros"-->
<!--              class="mr-2"-->
<!--              variant="outlined"-->
<!--              density="compact"-->
<!--              max-width="140"-->
<!--              hide-details-->
<!--            ></v-text-field>-->
<!--          </div>-->
        </template>
        <template #footer>
          <v-card
            class="ma-2"
            elevation="2"
            variant="flat"
            color="white"
          >
            Sugerencias rápidas (comming soon...)
          </v-card>
        </template>
        <template #rows_init="{ item }">
          <v-select
            v-model="item.participant"
            :items="all_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
          ></v-select>
        </template>
      </ToolbarCommon>
      <LocationsToolbar
        v-if="item"
        :full_main="item"
        main_collection_name="event"
        second_level
      />
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>