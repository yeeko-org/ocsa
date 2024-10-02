<script setup>

import SelectImpact from "~/components/dashboard/impact/SelectImpact.vue";
import { ref } from 'vue'

import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
const mainStore = useMainStore()

const { cats } = storeToRefs(mainStore)

const props = defineProps({
  mention: Object,
})


const addEvent = (mention, detail) => {
  mention.events.push({
    group: detail.id,
  })
}


</script>

<template>
  <v-toolbar
    color="grey-lighten-3"
    height="46"
  >
    <v-toolbar-title style="min-width: 300px;">
      Eventos ({{mention.events.length}})
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn
      v-for="group in cats.event_groups"
      :key="group.name"
      class="ml-2 text-none"
      color="green"
      stacked
      @click="addEvent(mention, group)"
    >
      <v-badge color="transparent" icon="add">
        <v-icon
          color="primary"
          :icon="group.icon"
        ></v-icon>
      </v-badge>
    </v-btn>
  </v-toolbar>
  <v-col
    cols="12"
    v-for="(event, index) in mention.events"
    :key="index"
  >
    <div class="d-flex">
      (Clasificaciones con selects)
    </div>
    <v-text-field
      v-model="event.description"
      label="Descripción (opcional)"
      variant="outlined"
      density="compact"
      hide-details
      style="width: 100%;"
    >
    </v-text-field>
    <v-divider class="mt-2"></v-divider>

  </v-col>
</template>

<style scoped>

</style>