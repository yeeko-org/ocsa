<script setup>
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})

const conflict_collection = computed(() => {
  return schemas.value.collections_dict['conflict']
})

const project_collection = computed(() => {
  return schemas.value.collections_dict['project']
})

const changeParentProject = (parent_project) => {
  props.full_main.parent_project = parent_project.id
  props.full_main.parent_project_full = parent_project
}

</script>


<template>
  <v-col cols="12" md="6" class="pa-0 d-flex">
    <v-text-field
      v-model="full_main.alternative_name"
      label="Nombres alternativos"
      variant="outlined"
      class="mr-2"
      style="max-width: 460px;"
    />
  </v-col>
  <v-col cols="12" md="6" class="pa-0 d-flex">
    <CardCommon
      :full_main="full_main.conflict && full_main.conflict_full"
      :collection_data="conflict_collection"
      is_simple
      class="mb-4"
      null_available
      title="Conflicto"
      @delete-item="full_main.conflict = null"
    />
  </v-col>
  <v-col cols="12" md="8" class="pa-0 d-flex">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="project_types"
      :width="300"
    />
  </v-col>
  <v-col cols="12" md="4" class="pa-0 d-flex">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="status_projects"
      :width="300"
    />
  </v-col>
  <v-col cols="12" md="4" class="pa-0 d-flex">
    <v-card
      variant="outlined" class="mr-2 px-2 mb-5"
      min-width="220"
    >
      <v-switch
        v-model="full_main.is_grouper"
        label="Es agrupador"
        append-icon="account_tree"
        hide-details
        color="primary"
      />
    </v-card>
  </v-col>
  <v-col cols="12" md="8" class="pa-0 d-flex mb-2">
    <CardCommon
      :full_main="full_main.parent_project && full_main.parent_project_full"
      :collection_data="project_collection"
      is_simple
      title="Proyecto agrupador"
      indirect_get
      null_available
      @selected-item="changeParentProject"
      @delete-item="full_main.parent_project = null"
    />
  </v-col>
</template>

<style scoped>

</style>