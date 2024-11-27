<script setup>
import { ref } from "vue";
import GenericSelectOld from "~/components/dashboard/common/GenericSelectOld.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

const props = defineProps({
  is_edit: Boolean,
  is_massive_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

const massive_edit_fields = [
    "impact_group",
    "status_validation",
]

const merge_fields = ref([])

</script>

<template>
  <v-row v-if="is_massive_edit">
    <v-col cols="12" class="d-flex align-center">
      <span
        class="mr-2 text-subtitle-1"
      >Campos a editar:</span>
      <v-chip-group
        v-model="merge_fields"
        class="mr-2"
        multiple
        color="accent"
      >
        <v-chip
          v-for="field in massive_edit_fields"
          :key="field"
          :value="field"
          filter
          variant="tonal"
        >
          {{ field }}
        </v-chip>
      </v-chip-group>
    </v-col>
  </v-row>
  <v-row>
    <v-col cols="12" class="d-flex">
      <v-text-field
        v-if="!is_massive_edit || merge_fields.includes('name')"
        v-model="full_main.name"
        label="Nombre del tipo de impacto"
        variant="outlined"
        style="max-width: 320px;"
      >
      </v-text-field>
      <v-text-field
        v-if="!is_massive_edit || merge_fields.includes('short_name')"
        v-model="full_main.short_name"
        label="Nombre corto"
        variant="outlined"
        style="max-width: 260px;"
        class="ml-2"
      >
      </v-text-field>
      <GenericSelectOld
        v-if="!is_massive_edit || merge_fields.includes('impact_group')"
        :final_filters="full_main"
        collection="impact_group"
        field="impact_group"
        label="Grupo de impacto"
        :clearable="false"
        style="max-width: 150px;"
        class="ml-2"
        density="default"
      />
      <v-switch
        v-if="!is_massive_edit"
        v-model="full_main.has_subtype"
        label="Tiene subtipos"
        color="primary"
        class="ml-4"
      >
      </v-switch>
    </v-col>
  </v-row>


</template>

<style scoped>

</style>