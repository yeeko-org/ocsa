<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  mention: Object,
})

const emits = defineEmits(['selected-item', 'search-item', 'edited-item'])

const actor_collection_data = computed(() => {
  return schemas.value.collections_dict['actor']
})

</script>

<template>
  <ToolbarCommon
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="participant_types"
    child_relation_name="participant"
    field="participants"
    two_columns
    :additional_fields="{'interests': []}"
    color="blue"
    emit_add
    @add-item="emits('search-item', $event)"
    required
  >
    <template #rows_init="{ item }">
      <CardCommon
        :full_main="item.actor_full"
        @edited-item="emits('edited-item', item)"
        _search-item="emits('search-item', item)"
        @selected-item="emits('selected-item', [item, $event])"
        :collection_data="actor_collection_data"
      />
<!--      <v-btn-->
<!--        v-else-->
<!--        color="accent"-->
<!--        variant="elevated"-->
<!--        @click="emits('search-item', item)"-->
<!--      >-->
<!--        Agregar participante-->
<!--      </v-btn>-->
    </template>
    <template #second-column="{ item }">
      <ToolbarCommon
        :main_object="item"
        main_collection_name="participant"
        filter_group_name="interest_types"
        child_relation_name="interest"
        field="interests"
        second_level
        color="cyan"
      >
        <template #rows="{ item }">
          <v-textarea
            v-model="item.text"
            label="Descripción del interés"
            variant="outlined"
            class="mr-8"
            density="compact"
            rows="1"
            auto-grow
          ></v-textarea>
        </template>
      </ToolbarCommon>
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>