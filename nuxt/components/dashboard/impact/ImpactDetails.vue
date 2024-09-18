<script setup>

import SelectImpact from "~/components/dashboard/impact/SelectImpact.vue";
import { ref, defineProps } from 'vue'

const props = defineProps({
  mention: Object,
})

const impact_details = [
  {name: "social", is_social: true, icon: "groups", color: "teal"},
  {name: "environmental", is_social: false, icon: "eco", color: "green"},
]

const addImpact = (mention, detail) => {
  mention.impacts.push({
    is_social: detail.is_social,
  })
}


</script>

<template>
  <v-toolbar
    color="grey-lighten-3"
    height="46"
  >
    <v-toolbar-title style="min-width: 300px;">
      Todas las afectaciones ({{mention.impacts.length}})
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn
      v-for="detail in impact_details"
      :key="detail.name"
      class="ml-2 text-none"
      color="green"
      stacked
      @click="addImpact(mention, detail)"
    >
      <v-badge color="transparent" icon="add">
        <v-icon
          :color="detail.color"
          :icon="detail.icon"
        ></v-icon>
      </v-badge>
    </v-btn>
  </v-toolbar>
  <v-col
    cols="12"
    v-for="(impact, index) in mention.impacts"
    :key="index"
    class="d-flex"
  >
    <SelectImpact
      :final_filters="impact"
      show_group
      :clearable="false"
      density="default"
      label="Tipo de afectación"
      @delete-impact="mention.impacts.splice(index, 1)"
    />
  </v-col>
</template>

<style scoped>

</style>