<script setup>
// Búsqueda de actor por nombre (decisions §10). Componente personalizado:
// el fetch a /actor/ y el comportamiento real (aplicar el actor como filtro)
// llegan en la Sesión 4. Hoy es un stub que reserva su lugar en la UI.
</script>

<template>
  <v-autocomplete
    :items="[]"
    label="Buscar actor por nombre"
    density="compact"
    variant="outlined"
    hide-details
    no-filter
    prepend-inner-icon="search"
  >
    <template #no-data>
      <div class="text-caption text-medium-emphasis pa-3">
        La búsqueda de actores se conecta al backend en una próxima fase.
      </div>
    </template>
  </v-autocomplete>
</template>