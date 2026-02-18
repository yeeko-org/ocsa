<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";
const mainStore = useMainStore()

const {
  event_group_violence, event_group_show_purpose, cats
} = storeToRefs(mainStore)

const props = defineProps({
  is_edit: {
    type: Boolean,
    default: false,
    required: false,
  },
})

const full_main = defineModel({type: Object, required: true})

const purpose_options = computed(() => {
  const event_type_full = cats.value.event_type.find(
      event_type => event_type.id === full_main.value.event_type) || {}
  return cats.value.purpose.map(purpose => {
    const field = `purpose_${purpose.short_name}`
    const description = event_type_full[field] || purpose.description
    return {
      ...purpose,
      description
    }
  })
})

</script>

<template>
  <v-textarea
    v-if="!is_edit"
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
  <template v-if="full_main.event_group === event_group_violence.id">
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
  <template v-if="event_group_show_purpose.includes(full_main.event_group)">
    <div class="text-subtitle-1 mt-4 text-grey-darken-2">
      Intencionalidad del mecanismo:
    </div>
    <div class="d-flex mr-8">
      <GenericSelect
        v-model="full_main"
        level_name="purpose"
        :main_width="400"
        :items="purpose_options"
        required
      />
    </div>
  </template>
</template>

<style scoped>

</style>