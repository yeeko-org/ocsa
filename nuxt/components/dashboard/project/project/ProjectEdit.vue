<script setup>
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import CardCommon from "~/components/dashboard/common/generic/CardCommon.vue";

import UserSelect from "~/components/dashboard/custom_filters/UserSelect.vue";

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})

const emits = defineEmits(['item-saved'])

const changeParentProject = (parent_project) => {
  full_main.value.parent_project = parent_project.id
  full_main.value.parent_project_full = parent_project
}

function changeConflict(conflict) {
  full_main.value.conflict = conflict.id
  full_main.value.conflict_full = conflict
}

</script>


<template>
  <v-col cols="12" md="6" class="pa-0 d-flex" :order="col_order">
    <v-text-field
      v-model="full_main.alternative_name"
      label="Nombres alternativos"
      variant="outlined"
      class="mr-2"
      style="max-width: 460px;"
    />
  </v-col>
  <v-col cols="12" md="6" class="pa-0 d-flex" :order="col_order">
    <CardCommon
      :full_main="full_main.conflict && full_main.conflict_full"
      collection_name="conflict"
      is_simple
      class="mb-4"
      null_available
      title="Conflicto"
      @selected-item="changeConflict($event)"
      @delete-item="full_main.conflict = null"
    />
  </v-col>
  <v-col cols="12" md="8" class="pa-0 d-flex" :order="col_order">
    <SelectGroup
      v-model="full_main"
      filter_group_name="project_types"
      :width="300"
      required
    />
  </v-col>
  <v-col cols="12" md="4" class="pa-0 d-flex" :order="col_order">
    <SelectGroup
      v-model="full_main"
      filter_group_name="status_projects"
      :width="300"
    />
  </v-col>
  <v-col cols="12" md="6" class="pa-0 d-flex align-center" :order="col_order">
    <v-card
      variant="outlined"
      class="mr-2 px-2 mb-2"
      width="220"
    >
      <v-switch
        v-model="full_main.is_grouper"
        label="Es agrupador"
        append-icon="hub"
        hide-details
        color="primary"
      />
    </v-card>
    <UserSelect
      :final_filters="full_main"
      field="editors"
      label="Editores"
      readonly
      multiple
      chips
    />
  </v-col>
  <v-col cols="12" md="6" class="pa-0 d-flex mb-2" :order="col_order">
    <CardCommon
      :full_main="full_main.parent_project && full_main.parent_project_full"
      collection_name="project"
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