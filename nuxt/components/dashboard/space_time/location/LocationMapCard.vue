<script setup>

import {useLocationDraw} from "~/composables/useLocationDraw.js";
import GeoImportButton from
    "~/components/dashboard/space_time/location/GeoImportButton.vue";

const props = defineProps({
  location_type: {
    type: String,
    required: true,
    validator: (value) => ['point', 'line', 'polygon'].includes(value)
  },
  full_main: Object,
  close_position: Object,
  can_expand: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits([
  'update:location', 'close', 'imported', 'import-error']);

const is_expanded = defineModel('expanded', {type: Boolean, default: false});

const mapContainer = ref(null);

const {location_type_full, isSatelliteView, toggleMapStyle, resize} =
    useLocationDraw({
      location_type: toRef(props, 'location_type'),
      full_main: toRef(props, 'full_main'),
      close_position: toRef(props, 'close_position'),
      container: mapContainer,
      onUpdate: (feature) => emit('update:location', feature),
    });

watch(is_expanded, resize);

</script>

<template>
  <v-card>
    <v-card-title class="text-headline-small d-flex">
      {{ full_main.id ? 'Editar' : 'Agregar' }}
      {{ location_type_full.name || 'Ubicación' }}
      <v-switch
        v-model="isSatelliteView"
        color="primary"
        label="Vista satelital"
        hide-details
        density="compact"
        class="ml-3"
        @change="toggleMapStyle"
      ></v-switch>

      <v-spacer></v-spacer>
      <GeoImportButton
        @imported="emit('imported', $event)"
        @import-error="emit('import-error', $event)"
      />
      <v-btn
        v-if="can_expand"
        variant="text"
        icon
        @click="is_expanded = !is_expanded"
        v-tooltip:bottom="is_expanded ? 'Restaurar' : 'Expandir mapa'"
      >
        <v-icon>
          {{ is_expanded ? 'collapse_content' : 'expand_content' }}
        </v-icon>
      </v-btn>
      <v-btn
          variant="text" @click="emit('close')" icon
          v-tooltip:bottom="`Cerrar mapa`"
      >
        <v-icon>close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <div
        ref="mapContainer"
        style="width: 100%; height: 500px; border-radius: 4px;"
      ></div>
    </v-card-text>
  </v-card>
</template>
