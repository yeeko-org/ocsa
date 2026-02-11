<script setup>

const emits = defineEmits(['confirm-delete'])
const props = defineProps({
  is_saved: Boolean,
  // dialog_delete: Boolean,
});
const dialog_visible = defineModel({ type: Boolean, default: false });
const delete_text = defineModel('delete_text', {type: String, default: '' });

</script>

<template>
  <v-dialog
    v-model="dialog_visible"
    max-width="500"
  >
    <v-card>
      <v-card-title>
        ¿Confirmas la eliminación de este registro?
      </v-card-title>
      <v-card-subtitle>
        Esta acción no se puede deshacer
      </v-card-subtitle>
      <v-card-text>
        <v-row>
          <v-col
            v-if="is_saved"
            cols="12"
          >
            <v-text-field
              v-model="delete_text"
              label="Escribe 'eliminar' para confirmar"
              outlined
              dense
              clearable
            ></v-text-field>
          </v-col>
        </v-row>
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
          @click="emits('confirm-delete')"
        >
          Eliminar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>