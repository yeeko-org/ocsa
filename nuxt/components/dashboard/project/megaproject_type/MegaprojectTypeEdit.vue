<script setup>

import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})

const extractivism_types = computed(() => {
    return all_nodes.value.project_types.children.reduce((acc, pt) => {
      if (pt.data.is_mix)
        return acc
      return acc.concat(pt.data)
    }, [])
})

</script>

<template>
  <v-col cols="12" class="d-flex justify-end" :order="col_order">
    <GenericSelect
      v-model="full_main"
      level_name="extractivism_types"
      :items="extractivism_types"
      label="Tipos de extractivismo"
      is_multiple
    />
  </v-col>
</template>

<style scoped>

</style>