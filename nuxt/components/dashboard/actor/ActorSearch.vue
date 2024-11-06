<script setup>

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
})
const emit = defineEmits(['close-dialog'])
const dialog = ref(false)
function saveActor() {
  console.log('saveActor')
}
</script>

<template>
  <v-card>
    <v-card-title class="text-h5 d-flex">
      <span v-if="!full_main.id">
        Nuevo actor
      </span>
      <span v-else>
        Editar actor
      </span>
      <v-spacer></v-spacer>
      <v-btn
        icon="close"
        variant="text"
        @click="emit('close-dialog')"
      >
      </v-btn>
    </v-card-title>
    <v-card-text>
      <v-text-field
        v-model="full_main.name"
        label="Nombre del actor"
        variant="outlined"
        class="mb-2"
      />
      <v-text-field
        v-model="full_main.official_name"
        label="Nombre oficial del actor"
        variant="outlined"
        class="mb-2"
      />
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="blue darken-1" variant="text" @click="dialog = false">Cancelar</v-btn>
      <v-btn color="blue darken-1" variant="text" @click="saveActor">Guardar</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>

</style>