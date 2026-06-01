<script setup>
import { useDisplay } from 'vuetify'
import { useMapStore } from '~/store/map.js'
import MapFilterPicker from '~/components/map/MapFilterPicker.vue'
import MapFilterActors from '~/components/map/MapFilterActors.vue'

// Rail de íconos de filtro (decisions §4): vertical en el borde izquierdo
// (escritorio), tira horizontal arriba (móvil). El extractivismo es el
// primer ícono y es especial: no abre un picker, sino que muestra/oculta su
// leyenda de chips de color (MainFilterMap). El resto son MapFilterPicker.
const { smAndDown } = useDisplay()
const mapStore = useMapStore()

// Definición declarativa de los filtros con picker. `optionsKey` apunta al
// getter del store con sus opciones; `key` a la rama de mapStore.filters.
const FILTER_DEFS = [
  {
    key: 'megaproject', label: 'Tipo de megaproyecto', icon: 'factory',
    pickerType: 'autocomplete', indented: true, dependsOn: 'extractivism',
    optionsKey: 'megaprojectOptions',
  },
  {
    key: 'violence', label: 'Violencia', icon: 'warning',
    pickerType: 'checkbox', optionsKey: 'violenceOptions',
  },
  {
    key: 'collectiveActions', label: 'Acciones colectivas', icon: 'campaign',
    pickerType: 'checkbox', optionsKey: 'collectiveActionOptions',
  },
  {
    key: 'legal', label: 'Mecanismos legales', icon: 'gavel',
    pickerType: 'checkbox', purposeToggle: true, optionsKey: 'legalOptions',
  },
  {
    key: 'socialImpacts', label: 'Afectaciones sociales', icon: 'diversity_3',
    pickerType: 'checkbox', optionsKey: 'socialImpactOptions',
  },
  {
    key: 'environmentalImpacts', label: 'Afectaciones ambientales',
    icon: 'forest', pickerType: 'checkbox',
    optionsKey: 'environmentalImpactOptions',
  },
  {
    key: 'states', label: 'Entidad federativa', icon: 'map',
    pickerType: 'autocomplete', optionsKey: 'stateOptions',
  },
]
</script>

<template>
  <client-only>
    <v-sheet
      :class="['map-filter-rail', smAndDown ? 'rail-horizontal' : 'rail-vertical']"
      color="#FFFFFFE6"
      rounded="lg"
      elevation="6"
    >
      <!-- Extractivismo: primer ícono, togglea su leyenda de color (§5). -->
      <div class="rail-btn">
        <v-badge
          :model-value="mapStore.filters.extractivism.length > 0"
          dot
          color="primary"
          offset-x="6"
          offset-y="6"
        >
          <v-btn
            icon="category"
            :color="mapStore.showExtractivismLegend ? 'primary' : undefined"
            variant="text"
            density="comfortable"
            @click="mapStore.showExtractivismLegend =
              !mapStore.showExtractivismLegend"
          />
        </v-badge>
        <v-tooltip
          activator="parent"
          text="Tipos de extractivismo (leyenda)"
          location="end"
        />
      </div>

      <!-- Resto de filtros con picker. -->
      <MapFilterPicker
        v-for="def in FILTER_DEFS"
        :key="def.key"
        :def="def"
        :options="mapStore[def.optionsKey]"
        v-model="mapStore.filters[def.key]"
      />

      <!-- Grupo de actores + posiciones (decisions §10). -->
      <MapFilterActors/>
    </v-sheet>
  </client-only>
</template>

<style scoped>
.map-filter-rail {
  position: absolute;
  z-index: 2;
  display: flex;
  align-items: center;
  padding: 4px;
}

/* Escritorio: columna vertical en el borde izquierdo, bajo la barra
   superior (logo + buscador + leyenda). */
.rail-vertical {
  left: 8px;
  top: 76px;
  flex-direction: column;
  gap: 2px;
}

/* Móvil: tira horizontal arriba, bajo la isla y los chips de extractivismo.
   El `top` es tentativo; el encaje fino del responsive es de la Sesión 5. */
.rail-horizontal {
  left: 8px;
  right: 8px;
  top: 112px;
  flex-direction: row;
  gap: 2px;
  overflow-x: auto;
}

.rail-btn {
  display: flex;
  align-items: center;
}
</style>
