<script setup>

// Botón de un solo uso: cada aviso se guarda como comentario una vez.
defineProps({
  done: Boolean,
})

defineEmits(['persist'])

</script>

<template>
  <v-btn
    icon
    size="x-small"
    variant="text"
    :disabled="done"
    @click="$emit('persist')"
    v-tooltip:bottom="done
      ? 'Ya se guardó como comentario'
      : 'Guardar como comentario'"
  >
    <v-icon size="small">
      {{ done ? 'check' : 'add_comment' }}
    </v-icon>
  </v-btn>
</template>
