<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import DescriptionIcon from "~/components/dashboard/utils/DescriptionIcon.vue";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  mention: Object,
})

const mainToolbarRef = ref(null)
const secondToolbarRef = ref(null)

const emits = defineEmits(['selected-item', 'search-item', 'edited-item'])
defineExpose({ resetInitialData })

const actor_collection_data = computed(() => {
  return schemas.value.collections_dict['actor']
})

function resetInitialData(){
  if (mainToolbarRef.value)
    mainToolbarRef.value.resetInitialData()
  if (secondToolbarRef.value)
    secondToolbarRef.value.resetInitialData()
}

</script>

<template>
  <ToolbarCommon
    ref="mainToolbarRef"
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="participant_types"
    child_relation_name="participant"
    field="participants"
    two_columns
    :additional_fields="{'interests': []}"
    color="blue"
    special_multiple
    emit_add
    required_full_category
    @add-item="emits('search-item', $event)"
    required
  >
    <template #rows_init="{ item, in_edition }">
      <CardCommon
        :full_main="item.actor_full"
        @edited-item="emits('edited-item', item)"
        @selected-item="emits('selected-item', [item, $event])"
        indirect_get
        :is_display="!in_edition"
        :is_simple="!in_edition"
        :collection_data="actor_collection_data"
      />
    </template>
    <template #second-column="{ item, in_edition }">
      <ToolbarCommon
        ref="secondToolbarRef"
        :main_object="item"
        main_collection_name="participant"
        filter_group_name="interest_types"
        child_relation_name="interest"
        required_full_category
        field="interests"
        second_level
        color="cyan"
        :external_in_edition="in_edition"
      >
        <template #rows="{ item, in_edition }">
          <v-textarea
            v-if="in_edition"
            v-model="item.text"
            label="Descripción del interés"
            variant="outlined"
            class="mr-8"
            density="compact"
            rows="1"
            auto-grow
          ></v-textarea>
          <DescriptionIcon
            v-else
            :description="item.text"
          />

        </template>
      </ToolbarCommon>
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>