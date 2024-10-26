<script setup>

import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";
const props = defineProps({
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
  <v-text-field
    v-model="full_main.section"
    label="Sección"
    variant="outlined"
    class="mr-2"
    style="width: 200px;"
  >
  </v-text-field>
  <v-text-field
    v-model="full_main.link"
    label="Enlace a la nota"
    variant="outlined"
    class="mr-2"
    style="width: 600px;"
  >
  </v-text-field>
  <StatusDetail
    :final_filters="full_main"
    field="status_register"
    collection="register"
    label="Status de registro"
    style="max-width: 300px;"
    density="default"
  />
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