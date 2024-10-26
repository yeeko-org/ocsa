<script setup>
import { ref } from "vue";
import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
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
        v-if="!is_massive_edit || merge_fields.includes('order')"
        v-model="full_main.order"
        label="Orden"
        type="number"
        variant="outlined"
        class="mr-2"
        style="max-width: 80px;"
      >
      </v-text-field>
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
      <GenericSelect
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
      <v-checkbox
        v-if="false"
        v-model="full_main.has_subtype"
        label="¿Tiene subtipos?"
        class="ml-2"
      />
      <StatusDetail
        v-if="!is_massive_edit || merge_fields.includes('status_validation')"
        :final_filters="full_main"
        field="status_validation"
        collection="validation"
        label="Status de validación"
        style="max-width: 300px;"
        class="ml-2"
        density="default"
        :clearable="false"
      />
    </v-col>
    <v-col cols="12">
      <v-textarea
        v-if="!is_massive_edit || merge_fields.includes('description')"
        v-model="full_main.description"
        rows="2"
        auto-grow
        label="Descripción"
        variant="outlined"
        hide-details
        class="mt-2"
      >
      </v-textarea>
    </v-col>
    <v-col cols="12">
      <v-textarea
        v-if="!is_massive_edit || merge_fields.includes('help_text')"
        v-model="full_main.help_text"
        label="Texto de ayuda"
        variant="outlined"
        class="mt-2"
        rows="2"
        auto-grow
        _hide-details
      >
      </v-textarea>
    </v-col>
  </v-row>


</template>

<style scoped>

</style>