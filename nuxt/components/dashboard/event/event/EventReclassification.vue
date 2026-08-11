<script setup>

import dayjs from "dayjs";
import {useMainStore} from "~/store/index.js";

const full_main = defineModel({type: Object, required: true})

const mainStore = useMainStore()
const { patchSimple, showSnackbar } = mainStore

const saving = ref(false)

// --- Mapeos estáticos de etiquetas (todo sale de reclassification_data) ---
const STAGE_META = {
  pending:      { label: 'Pendiente',     color: 'grey',
                  icon: 'hourglass_empty' },
  reclassified: { label: 'Reclasificado', color: 'blue',
                  icon: 'auto_awesome' },
  problematic:  { label: 'Problemático',  color: 'deep-orange',
                  icon: 'report_problem' },
  confirmed:    { label: 'Confirmado',    color: 'green',
                  icon: 'verified' },
  discarded:    { label: 'Descartado',    color: 'blue-grey',
                  icon: 'cancel' },
}
const PURPOSE_LABELS = { spoliation: 'Despojo', defense: 'Defensa' }
const PURPOSE_ID_LABELS = { 1: 'Despojo', 2: 'Defensa' }
const GROUP_ID_LABELS = {
  1: 'Violencias', 2: 'Acciones colectivas', 3: 'Mecanismos legales' }
const ACTUAL_GROUP_LABELS = {
  acts_of_violence: 'Violencia', collective_actions: 'Acción colectiva' }

const ROWS = [
  { key: 'group',       label: 'Grupo' },
  { key: 'event_type',  label: 'Tipo de evento' },
  { key: 'purpose',     label: 'Intencionalidad' },
  { key: 'description', label: 'Descripción' },
]

const stage = computed(() => full_main.value.reclassification_stage)
const stage_meta = computed(() =>
  STAGE_META[stage.value] || { label: stage.value, color: 'grey',
    icon: 'help' })

const confidence = computed(() =>
  full_main.value.reclassification_confidence)
const confidence_color = computed(() => {
  const c = confidence.value
  if (c == null) return 'grey'
  if (c < 70) return 'red'
  if (c < 90) return 'amber'
  return 'green'
})

const data = computed(() => full_main.value.reclassification_data || {})
const original = computed(() => data.value.original || {})
const ai = computed(() => data.value.ai || {})

function norm(s) {
  return (s ?? '').toString().trim().toLowerCase()
}

const original_view = computed(() => ({
  group: GROUP_ID_LABELS[original.value.event_group_id] ?? '—',
  event_type: original.value.event_type ?? '—',
  purpose: PURPOSE_ID_LABELS[original.value.purpose_id] ?? 'n/a',
  description: original.value.description || '—',
}))
const ai_view = computed(() => ({
  group: 'Mecanismos legales',
  event_type: ai.value.event_type ?? '—',
  purpose: PURPOSE_LABELS[ai.value.purpose] ?? '—',
  description: ai.value.description || '—',
}))

const columns = computed(() => [
  { title: 'Antes (original)', color: 'grey',
    view: original_view.value },
  { title: 'Después (propuesta IA)', color: 'blue',
    view: ai_view.value },
])

// Resalta diferencias entre original y propuesta de la IA.
const diff = computed(() => ({
  event_type: norm(original.value.event_type)
    !== norm(ai.value.event_type),
  purpose: (PURPOSE_ID_LABELS[original.value.purpose_id] ?? null)
    !== (PURPOSE_LABELS[ai.value.purpose] ?? null),
  description: (original.value.description || '').trim()
    !== (ai.value.description || '').trim(),
}))

const actual_group_label = computed(() =>
  ACTUAL_GROUP_LABELS[ai.value.actual_group] || null)

const reclassified_at = computed(() => {
  const raw = data.value.reclassified_at
  return raw ? dayjs(raw).format('DD/MM/YYYY HH:mm') : null
})

async function setStage(new_stage) {
  saving.value = true
  const res = await patchSimple(
    ['event', full_main.value.id,
      { reclassification_stage: new_stage }])
  saving.value = false
  if (res.errors) {
    showSnackbar('No se pudo actualizar la reclasificación')
    return
  }
  full_main.value.reclassification_stage = new_stage
  showSnackbar(new_stage === 'confirmed'
    ? 'Reclasificación confirmada'
    : 'Reclasificación descartada')
}

</script>

<template>
  <v-card variant="outlined" class="mb-4 pa-3">

    <div class="d-flex align-center flex-wrap mb-3">
      <v-chip
        :color="stage_meta.color"
        variant="flat"
        label
        class="mr-2"
      >
        <v-icon start>{{ stage_meta.icon }}</v-icon>
        {{ stage_meta.label }}
      </v-chip>
      <v-chip
        v-if="confidence != null"
        :color="confidence_color"
        variant="tonal"
        label
        size="small"
        class="mr-2"
      >
        <v-icon start size="small">target</v-icon>
        Confianza: {{ Math.round(confidence) }}%
      </v-chip>
      <v-spacer />
      <span v-if="reclassified_at" class="text-body-small text-grey">
        Reclasificado: {{ reclassified_at }}
      </span>
    </div>

    <v-alert
      v-if="stage === 'problematic'"
      type="warning"
      variant="tonal"
      density="comfortable"
      class="mb-3"
    >
      <div class="font-weight-bold" v-if="actual_group_label">
        La IA considera que esto es: {{ actual_group_label }}
      </div>
      <div class="font-weight-bold" v-else>
        La IA no pudo resolver un tipo de mecanismo legal válido.
      </div>
      <div class="text-body-medium mt-1">
        El tipo del evento NO se modificó (conserva los valores
        anteriores).
      </div>
    </v-alert>

    <v-row dense>
      <v-col
        v-for="col in columns"
        :key="col.title"
        cols="12"
        md="6"
      >
        <div class="text-label-small">{{ col.title }}</div>
        <v-card variant="tonal" :color="col.color" class="pa-2">
          <div
            v-for="row in ROWS"
            :key="row.key"
            class="py-1"
            :class="{ 'reclass-diff': diff[row.key] }"
          >
            <div class="text-body-small text-medium-emphasis">
              {{ row.label }}
            </div>
            <div
              class="text-body-medium"
              :class="{ 'font-weight-bold': diff[row.key] }"
            >
              {{ col.view[row.key] }}
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <div v-if="stage === 'reclassified'" class="d-flex mt-3">
      <v-btn
        color="green"
        variant="flat"
        :loading="saving"
        class="mr-2"
        @click="setStage('confirmed')"
      >
        <v-icon start>check</v-icon>
        Confirmar
      </v-btn>
      <v-btn
        color="red"
        variant="outlined"
        :loading="saving"
        @click="setStage('discarded')"
      >
        <v-icon start>close</v-icon>
        Descartar
      </v-btn>
    </div>

  </v-card>
</template>

<style scoped>
.reclass-diff {
  border-left: 3px solid #f9a825;
  padding-left: 8px;
  margin-left: -3px;
}
</style>