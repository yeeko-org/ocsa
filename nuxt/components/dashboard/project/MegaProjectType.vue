<script setup>
import { ref, computed } from 'vue'
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const props = defineProps({
  project: Object,
})
const { cats, megaproject_types, extractivism_types } = storeToRefs(mainStore)

const extract_type_set = ref(null)

const full_mp_type = computed(() => {
  return megaproject_types.value.find(mp_type => {
    return mp_type.id === props.project.megaproject_type
  })
})

const filtered_mp_types = computed(() => {
  if (!full_mp_type.value)
    return megaproject_types.value
  if (!full_mp_type.value.extractivism_obj)
    return megaproject_types.value
  // const mp_type = props.project.megaproject_type
  return megaproject_types.value.filter(mp_type => {
    return !mp_type.extractivism_obj
      ? false
      : full_mp_type.value.extractivism_obj.id === mp_type.extractivism_obj.id
  })
})
// all_parameter_groups(){
//   if (this.show_empty)
//     return [{id: 0, name: "Vacíos"}].concat(this.cats.parameter_groups)
//   return this.cats.parameter_groups
// },

const all_extractivism_types = computed(() =>
  Object.values(extractivism_types.value) )


const extractivism_type = computed({
  get: () => {
    if (extract_type_set.value !== null)
      return extract_type_set.value
    else if (!full_mp_type.value)
      return null
    else if (full_mp_type.value.extractivism_obj)
      return full_mp_type.value.extractivism_obj.id
    else
      return null
  },
  set: (value) => {
    extract_type_set.value = value
  }
})

const editExtractivismType = () => {
  console.log("editExtractivismType")
  // extract_type_set.value = null
}


</script>


<template>
  <v-row class="d-flex">
    <v-col cols="5">
      <v-select
        v-model="extractivism_type"
        :items="all_extractivism_types"
        item-title="name"
        item-value="id"
        _clearable="!project.megaproject_type"
        label="Tipo de Extractivismo"
        _class="mx-1"
        variant="outlined"
      >
        <template #append>
            <v-icon @click="editExtractivismType">edit</v-icon>
        </template>
      </v-select>
    </v-col>
    <v-col cols="7">
      <v-autocomplete
        :items="filtered_mp_types"
        v-model="project.megaproject_type"
        item-title="name"
        item-value="id"
        label="Tipo de Megaproyecto"
        _class="mx-1"
        clearable
      >
      </v-autocomplete>
    </v-col>
  </v-row>
</template>

<style scoped>

</style>