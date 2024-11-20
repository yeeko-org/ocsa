<script setup>
import dayjs from 'dayjs'

import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";
import SelectDate from "~/components/dashboard/common/SelectDate.vue";
const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

// const addMention = () => {
//   console.log("add mention")
//   if (!props.full_main.mentions) {
//     props.full_main.mentions = []
//   }
//   props.full_main.mentions.push({})
// }

function editDate(date) {
  console.log("edit date", date)
  props.full_main.date = dayjs(date).format('YYYY-MM-DD')
}

</script>

<template>
  <v-text-field
    v-model="full_main.title"
    label="Título de la nota"
    variant="outlined"
    style="width: 100%;"
  >
  </v-text-field>
  <div class="d-flex" style="width: 100%;">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="source_types"
    />
    <v-text-field
      v-model="full_main.section"
      label="Sección"
      variant="outlined"
      class="ml-2"
      style="width: 200px;"
    >
    </v-text-field>
    <SelectDate
      v-if="false"
      :init_date="full_main.date"
      @update:date="editDate($event)"
    />
    <v-date-input
      v-if="false"
      v-model="full_main.date"
      label="Select a date"
      show-adjacent-months
      max-width="368"
    ></v-date-input>
    <v-date-picker
      v-if="false"
      color="accent"
      v-model="full_main.date_raw"
      show-adjacent-months
      cancel-text="Cancelar"
      ok-text="Guardar"
      title="Selecciona una fecha"
    >
    </v-date-picker>
    <v-date-input
      v-if="true"
      v-model="full_main.date_raw"
      @update:modelValue="editDate"
      label="Fecha de la nota"
      class="ml-2"
      max-width="368"
    ></v-date-input>
  </div>
  <v-text-field
    v-model="full_main.link"
    label="Enlace a la nota"
    variant="outlined"
    class="mr-2"
    style="width: 600px;"
  >
  </v-text-field>
</template>

<style scoped>

</style>