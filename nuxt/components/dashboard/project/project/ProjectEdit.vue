<script setup>
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import CardCommon from "~/components/dashboard/common/generic/CardCommon.vue";
import DialogEdit from "~/components/dashboard/common/dialog/DialogEdit.vue";
import CardComponent from "~/components/dashboard/common/CardComponent.vue";

import UserSelect from "~/components/dashboard/custom_filters/UserSelect.vue";
import { useMainStore } from "~/store/index.js";
import { storeToRefs } from "pinia";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

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

const conflict_collection_data = computed(
  () => schemas.value.collections_dict?.conflict)

const dialog_create_open = ref(false)
const new_conflict_data = ref(null)

function openCreateDialog() {
  new_conflict_data.value = {
    name: full_main.value.name,
    status_validation: 'validated',
  }
  dialog_create_open.value = true
}

function onConflictCreated({res}) {
  if (!res) return
  dialog_create_open.value = false
  changeConflict(res)
}

const dialog_inherit_open = ref(false)
const parent_conflict_full = ref(null)
const loading_parent_conflict = ref(false)

async function openInheritDialog() {
  dialog_inherit_open.value = true
  parent_conflict_full.value = null
  loading_parent_conflict.value = true
  const parent_conflict_id =
    full_main.value.parent_project_full?.conflict
  parent_conflict_full.value = await mainStore.getSimple(
    ['conflict', parent_conflict_id])
  loading_parent_conflict.value = false
}

function confirmInherit() {
  if (!parent_conflict_full.value) return
  changeConflict(parent_conflict_full.value)
  dialog_inherit_open.value = false
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
    >
      <template #buttons v-if="!full_main.conflict">
        <v-btn
          icon="wand_stars"
          size="small"
          color="primary"
          variant="outlined"
          @click="openCreateDialog"
          v-tooltip="`Crear automáticamente`"
        />
        <v-btn
          v-if="full_main.parent_project_full?.conflict"
          icon="family_history"
          size="small"
          color="primary"
          variant="outlined"
          @click="openInheritDialog"
          v-tooltip="`Usar conflicto del Proyecto agrupador`"
        />
      </template>
    </CardCommon>
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
  <DialogEdit
    v-if="conflict_collection_data"
    v-model="new_conflict_data"
    v-model:open="dialog_create_open"
    :collection_data="conflict_collection_data"
    @item-saved="onConflictCreated"
  />
  <v-dialog v-model="dialog_inherit_open" max-width="800">
    <v-card>
      <v-card-title class="text-headline-small d-flex">
        Heredar conflicto del Proyecto agrupador
        <v-spacer></v-spacer>
        <v-btn
          icon="close"
          variant="text"
          @click="dialog_inherit_open = false"
        ></v-btn>
      </v-card-title>
      <v-card-text>
        <div
          v-if="loading_parent_conflict"
          class="d-flex justify-center pa-4"
        >
          <v-progress-circular indeterminate color="primary" />
        </div>
        <CardComponent
          v-else-if="parent_conflict_full && conflict_collection_data"
          :full_main="parent_conflict_full"
          :collection_data="conflict_collection_data"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          @click="dialog_inherit_open = false"
        >
          Cancelar
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :disabled="!parent_conflict_full"
          @click="confirmInherit"
        >
          Confirmar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>