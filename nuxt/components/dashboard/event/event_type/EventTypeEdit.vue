<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()

const { event_group_show_purpose } = storeToRefs(mainStore)

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})
const emits = defineEmits(['item-saved'])

</script>

<template>
  <v-col
    cols="12"
    class="px-0"
    order="4"
  >
    <SelectGroup
      v-model="full_main"
      filter_group_name="event_types"
      main_collection_name="event_type"
      field="event_group"
      forced_level="subtype"
      :width="340"
      required
    />
  </v-col>
  <template v-if="event_group_show_purpose.includes(full_main.event_group)">
    <v-col cols="12" class="px-0" order="10">
      <v-textarea
        v-model="full_main.purpose_defense"
        label="Explicación del mecanismo legal de defensa"
        variant="outlined"
        rows="1"
        auto-grow
        hide-details
      >
      </v-textarea>
    </v-col>
    <v-col cols="12" class="px-0 pb-8" order="11">
      <v-textarea
        v-model="full_main.purpose_spoliation"
        label="Explicación del mecanismo legal de despojo"
        variant="outlined"
        rows="1"
        auto-grow
        hide-details
      >
      </v-textarea>
    </v-col>
  </template>
  <v-col
    v-else
    cols="12"
    class="d-flex pa-0"
    order="10"
  >
    <v-switch

      v-model="full_main.has_displacement"
      label="Desplegar Desplazamiento Forzado"
      class="mt-2"
      color="accent"
      append-icon="hiking"
    />
  </v-col>

</template>

<style scoped>

</style>