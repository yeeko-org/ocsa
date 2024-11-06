<script setup>
import dayjs from 'dayjs'

import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";
const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

const addMention = () => {
  console.log("add mention")
  if (!props.full_main.mentions) {
    props.full_main.mentions = []
  }
  props.full_main.mentions.push({})
}

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
  <GenericSelect
    v-if="false"
    :final_filters="full_main"
    collection="sources"
    field="source"
    label="Medio o fuente"
    clearable
    hide_details
    style="width: 200px;"
    class="mr-2"
    density="default"
  />
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
<!--    <SelectDate-->
<!--      :init_date="full_main.date"-->
<!--      @update:date="editDate($event)"-->
<!--    />-->
    <v-date-input
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
<!--  <v-card v-if="full_main">-->
<!--    <v-card-title>-->
<!--      <div class="d-flex">-->
<!--        {{ full_main.mentions.length }} menciones de proyectos-->
<!--        <v-spacer></v-spacer>-->
<!--        <v-btn-->
<!--          @click="addMention"-->
<!--          color="primary"-->
<!--          variant="outlined"-->
<!--          prepend-icon="add"-->
<!--          text="Agregar mención"-->
<!--        ></v-btn>-->
<!--      </div>-->
<!--    </v-card-title>-->
<!--    <v-card-text>-->
<!--      <v-row>-->
<!--        <MentionDetails-->
<!--          v-for="mention in full_main.mentions"-->
<!--          :key="mention.id"-->
<!--          :mention="mention"-->
<!--          is_full-->
<!--        />-->
<!--      </v-row>-->
<!--    </v-card-text>-->
<!--  </v-card>-->
</template>

<style scoped>

</style>