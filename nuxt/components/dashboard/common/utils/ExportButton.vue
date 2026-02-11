<script setup>

const emits = defineEmits(['export-records'])

const props = defineProps({
  loadingExport: {
    type: Boolean,
    default: false,
  }
})

</script>

<template>
  <v-menu
    location="bottom"
  >
    <template v-slot:activator="{ props }">
      <v-btn
        v-bind="props"
        color="green"
        variant="elevated"
        dark
        append-icon="table_chart"
        :loading="loadingExport"
      >
        Descargar
      </v-btn>
    </template>
    <v-list>
      <v-list-item
        title="Todos los registros"
        @click="emits('export-records', true)"
      >
        <template v-slot:prepend>
          <v-icon icon="filter_list_off" color="grey"></v-icon>
        </template>
      </v-list-item>
      <v-list-item
        title="Solo filtrados"
        @click="emits('export-records', false)"
      >
        <template v-slot:prepend>
          <v-icon icon="filter_list" color="accent"></v-icon>
        </template>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<style scoped>

</style>