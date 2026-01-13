<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import DescriptionIcon from "~/components/dashboard/utils/DescriptionIcon.vue";
const mainStore = useMainStore()

const {
  event_group_violence, event_group_show_position,
} = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_edit: {
    type: Boolean,
    default: false,
    required: false,
  },
  in_edition: {
    type: Boolean,
    default: null,
    required: false,
  },
})


</script>

<template>
  <v-textarea
    v-if="!is_edit && in_edition"
    v-model="full_main.description"
    label="Descripción del evento (opcional)"
    variant="outlined"
    density="compact"
    rows="1"
    hide-details
    auto-grow
    style="width: 100%; max-width: 600px;"
  >
  </v-textarea>
  <DescriptionIcon
    v-else-if="!is_edit"
    :description="full_main.description"
  />
  <template v-if="full_main.event_group === event_group_violence.id">
    <template v-if="is_edit">
      <div class="text-subtitle-1 mt-4">Número de víctimas:</div>
      <div class="d-flex mr-8">
        <v-text-field
          v-model="full_main.number_women"
          type="number"
          label="Mujeres"
          class="mr-2"
          variant="outlined"
          density="compact"
          max-width="140"
          hide-details
        ></v-text-field>
        <v-text-field
          v-model="full_main.number_men"
          type="number"
          label="Hombres"
          class="mr-2"
          variant="outlined"
          density="compact"
          max-width="140"
          hide-details
        ></v-text-field>
        <v-text-field
          v-model="full_main.number_mix"
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

    <div v-else class="d-flex ml-2 text-body-2 align-center">
      <div class="text-subtitle-1 mr-2">Víctimas:</div>
      <div class="mr-2">
        <strong>Mujeres:</strong> {{ full_main.number_women || 0 }}
      </div>
      <div class="mr-2">
        <strong>Hombres:</strong> {{ full_main.number_men || 0 }}
      </div>
      <div class="mr-2">
        <strong>Otros:</strong> {{ full_main.number_mix || 0 }}
      </div>
    </div>
  </template>
  <template v-if="event_group_show_position.includes(full_main.event_group)">
    <div class="text-subtitle-1 mt-4" v-if="false">Intencionalidad:</div>
    <div class="d-flex" :class="in_edition ? 'mr-8 mt-5' : ''">
      <SelectGroup
        :main_object="full_main"
        filter_group_name="purposes"
        main_collection_name="event"
        :is_display="!in_edition"
      />
    </div>
  </template>
</template>

<style scoped>

</style>