<script setup>
import { ref } from "vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

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
        v-if="!is_massive_edit || merge_fields.includes('short_name')"
        v-model="full_main.short_name"
        label="Nombre corto"
        variant="outlined"
        style="max-width: 260px;"
        class="mx-2"
      >
      </v-text-field>
      <SelectGroup
        filter_group_name="impact_types"
        :main_object="full_main"
        forced_level="type"
        main_collection_name="impact_type"
        subtype_class="ml-6"
      />
      <v-switch
        v-if="!is_massive_edit && false"
        v-model="full_main.has_subtype"
        label="Tiene subtipos"
        color="primary"
        class="ml-4"
      >
      </v-switch>
      <v-switch
        v-model="full_main.has_displacement"
        label="Desplegar Desplazamiento Forzado"
        class="ml-4"
        color="accent"
        append-icon="hiking"
      />

    </v-col>
  </v-row>


</template>

<style scoped>

</style>