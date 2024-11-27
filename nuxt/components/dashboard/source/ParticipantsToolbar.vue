<script setup>

import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";

const props = defineProps({
  mention: Object,
})

const emits = defineEmits(['search-item', 'edit-item'])

</script>

<template>
  <ToolbarCommon
    v-if="true"
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
      <v-card
        v-if="item.actor_full"
        class="d-flex align-center px-3"
        color="blue"
        variant="tonal"
        style="width: 100%;"
      >
        <ActorCard
          :full_main="item.actor_full"
        />
        <v-spacer></v-spacer>
        <div class="d-flex flex-column">
          <v-btn
            icon="edit"
            @click="emits('edit-item', item)"
            size="small"
            color="accent"
            variant="outlined"
          ></v-btn>
          <v-btn
            icon="cached"
            @click="emits('search-item', item)"
            size="small"
            color="accent"
            variant="outlined"
          ></v-btn>
        </div>
      </v-card>
      <v-btn
        v-else
        color="accent"
        variant="elevated"
        @click="emits('search-item', item)"
      >
        Agregar participante
      </v-btn>
    </template>
    <template #second-column="{ item }">
      <ToolbarCommon
        v-if="true"
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
      <v-divider class="mt-8" v-if="false"></v-divider>
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>