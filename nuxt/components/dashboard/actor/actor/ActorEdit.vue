<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";
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

const actor_collection_data = computed(() => {
  return schemas.value.collections_dict['actor']
})

const changeParentActor = (parent_actor) => {
  props.full_main.parent_actor = parent_actor.id
  props.full_main.parent_actor_full = parent_actor
}

</script>

<template>
  <v-col cols="12" class="d-flex pa-0">
    <v-text-field
      v-model="full_main.alternative_names"
      label="Nombres alternativos"
      variant="outlined"
      class="mb-2"
    />
  </v-col>
  <v-col cols="12" md="6" class="d-flex pa-0">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="sectors"
      main_collection_name="actor"
    />
  </v-col>
  <v-col cols="12" md="6" class="d-flex py-0 pl-0 pr-3 mb-2">
    <CardCommon
      :full_main="full_main.parent_actor && full_main.parent_actor_full"
      :collection_data="actor_collection_data"
      is_simple
      title="Actor padre"
      indirect_get
      null_available
      @selected-item="changeParentActor"
      @delete-item="full_main.parent_actor = null"
    />
  </v-col>
  <v-col cols="12" class="d-flex pa-0">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="belongs"
      main_collection_name="actor"
      field="belongs"
      :width="400"
      subtype_class="mr-2"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="indigenous_groups"
      main_collection_name="actor"
      field="indigenous_group"
      subtype_class="mr-2"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="countries"
      main_collection_name="actor"
      field="countries"
    />
  </v-col>
</template>

<style scoped>

</style>