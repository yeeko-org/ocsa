<script setup>
import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";
import {computed} from "vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

const main_collection = computed(() =>{
  // console.log("actor", schemas.value.collections_dict["actor"])
  return schemas.value.collections_dict["actor"]
})

</script>

<template>
  <v-col cols="12" class="d-flex pa-0">
    <v-text-field
      v-model="full_main.official_name"
      label="Nombre oficial del actor"
      variant="outlined"
      class="mb-2 mr-3"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="sectors"
      :main_collection="main_collection"
    />
  </v-col>
  <v-col cols="12" class="d-flex pa-0">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="belongs"
      :main_collection="main_collection"
      field="belongs"
      width="400"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="indigenous_groups"
      :main_collection="main_collection"
      field="indigenous_group"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="countries"
      :main_collection="main_collection"
      field="countries"
    />
  </v-col>
</template>

<style scoped>

</style>