<script setup>

import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";

import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})
</script>

<template>
  <v-col cols="12" class="pa-0 d-flex flex-wrap" :order="col_order">
    <GenericSelect
      v-model="full_main"
      level_name="states"
      :items="cats.state || []"
      label="Estados"
      class="mr-4"
      is_multiple
      is_autocomplete
      :main_width="460"
    />
    <v-checkbox
      v-model="full_main.is_official"
      label="Es del catálogo oficial del INPI"
      color="primary"
      hide-details
    />
  </v-col>
</template>

<style scoped>

</style>
