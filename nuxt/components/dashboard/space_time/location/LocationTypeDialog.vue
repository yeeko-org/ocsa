<script setup>

defineProps({
  // Qué se va a perder, ya redactado por useLocationGeometry
  discard_label: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['confirm'])

// Sin datos que perder no hay diálogo: cerrarlo sin decidir dejaría el
// cambio a medias, así que sólo se sale por Cancelar o por Cambiar.
const dialog_visible = defineModel({type: Boolean, default: false})

</script>

<template>
  <v-dialog
    v-model="dialog_visible"
    max-width="460"
    persistent
  >
    <v-card>
      <v-card-title>
        Cambiar el tipo de ubicación
      </v-card-title>
      <v-card-text>
        Cambiar el tipo descartará {{ discard_label }}. ¿Continuar?
      </v-card-text>
      <v-card-actions>
        <v-btn
          color="accent"
          variant="outlined"
          @click="dialog_visible = false"
        >
          Cancelar
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="error"
          variant="elevated"
          @click="emit('confirm')"
        >
          Cambiar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
