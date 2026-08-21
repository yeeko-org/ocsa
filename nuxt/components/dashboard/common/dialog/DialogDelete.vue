<script setup>

const emits = defineEmits(['confirm-delete'])
const props = defineProps({
  is_saved: Boolean,
  loading: Boolean,
  can_delete: {
    type: Boolean,
    default: true,
  },
  report_data: {
    type: Array,
    default: null,
  },
  delete_errors: {
    type: [Object, Array, String],
    default: null,
  },
});
const dialog_visible = defineModel({ type: Boolean, default: false });
const delete_text = defineModel('delete_text', {type: String, default: '' });

const affected_relations = computed(() => {
  if (!props.report_data) return []
  return props.report_data.filter(r => r.affected_records > 0)
})

const has_report = computed(() => affected_relations.value.length > 0)

const confirm_btn_text = computed(() =>
  has_report.value ? 'Sí, eliminar de todos modos' : 'Eliminar')

const formatted_errors = computed(() => {
  const e = props.delete_errors
  if (!e) return null
  if (typeof e === 'string') return e
  return JSON.stringify(e, null, 2)
})

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
        <v-alert
          v-if="has_report"
          type="warning"
          variant="tonal"
          class="mb-3"
        >
          <div class="font-weight-bold mb-1">
            Esta acción afectará otros registros:
          </div>
          <ul class="ml-4">
            <li
              v-for="rel in affected_relations"
              :key="rel.related_name"
            >
              {{ rel.affected_records }} {{ rel.related_name }}
            </li>
          </ul>
        </v-alert>
        <v-alert
          v-if="formatted_errors"
          type="error"
          variant="tonal"
          class="mb-3"
          style="white-space: pre-wrap;"
        >
          {{ formatted_errors }}
        </v-alert>
        <v-row>
          <v-col
            v-if="is_saved"
            cols="12"
          >
            <v-text-field
              v-model="delete_text"
              label="Escribe 'eliminar' para confirmar"
              variant="outlined"
              density="compact"
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
          v-if="can_delete"
          color="error"
          variant="elevated"
          :loading="loading"
          @click="emits('confirm-delete')"
        >
          {{ confirm_btn_text }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>