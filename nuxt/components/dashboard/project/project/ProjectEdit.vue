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

const dialog_search = ref(false)

function closeDialog(item) {
  dialog_search.value = false
  // props.full_main.project = item.id
  console.log("item", item)
}

const conflict_collection = computed(() => {
  return schemas.value.collections_dict['conflict']
})

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
    <v-card variant="outlined" class="mr-2 px-2 mb-5">
      <v-switch
        v-model="full_main.is_grouper"
        label="Es agrupador"
        append-icon="group_work"
        hide-details
        color="primary"
      />
    </v-card>
  </v-col>
  <v-col cols="12" md="6" class="pa-0 d-flex">
    <CardCommon
      :full_main="full_main.conflict && full_main.conflict_full"
      :collection_data="conflict_collection"
      is_simple
      class="mb-4"
      null_available
      @delete-item="full_main.conflict = null"
    />
  </v-col>
  <v-col cols="12" class="pa-0 d-flex">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="project_types"
      :width="360"
    />
  </v-col>
  <v-dialog
    v-model="dialog_search"
    max-width="920"
  >
    <v-card height="800">
      <v-card-text class="py-0">
        <CollectionDisplay
          :parent_collection="conflict_collection"
          is_mini
          @select-item="closeDialog($event)"
        />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>