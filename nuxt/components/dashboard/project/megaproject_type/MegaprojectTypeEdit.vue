<script setup>

import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

const extractivism_types = computed(() => {
    return all_nodes.value.project_types.children.reduce((acc, pt) => {
      if (pt.data.is_mix)
        return acc
      return acc.concat(pt.data)
    }, [])
})

</script>

<template>
  <v-row>
    <v-col cols="12" class="d-flex justify-end">
      <GenericSelect
        :main_object="full_main"
        level_name="extractivism_types"
        :items="extractivism_types"
        label="Tipos de extrativismo"
        is_multiple
      />
    </v-col>
  </v-row>
</template>

<style scoped>

</style>