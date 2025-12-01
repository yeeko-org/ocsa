<script setup >

import dayjs from "dayjs";
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/es'
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
dayjs.locale('es')
dayjs.extend(relativeTime)


const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

const emits = defineEmits(['item-saved'])

const { sendReprocessScrapedRecord } = mainStore

const total_days = computed(() => {
  const from_date = dayjs(props.full_main.from_date)
  const to_date = dayjs(props.full_main.to_date)
  return to_date.diff(from_date, 'day') + 1
})

function humanDate(date) {
  return dayjs(date).format('DD [de] MMMM [de] YYYY')
}

const from_date = computed(() => {
  return humanDate(props.full_main.from_date)
})

const to_date = computed(() => {
  return humanDate(props.full_main.to_date)
})

const ai_completed = computed(() => {
  return props.full_main.articles_count === props.full_main.preclassified_count
})

const avg_per_day = computed(() => {
  if (total_days.value > 0) {
    return (props.full_main.articles_count / total_days.value).toFixed(0)
  }
  return 0
})

const ready_count = computed(() => {
  return props.full_main.pre_selected - props.full_main.pending_count
})

function sendReprocess() {
  sendReprocessScrapedRecord(props.full_main.id).then(response => {
    // console.log("response sendReprocess", response)
  })
}

</script>

<template>
  <v-col cols="7" class="d-flex pa-0">
    <v-list>
      <v-list-item prepend-icon="calendar_today">
          <v-list-item-title class="_text-h6">
            {{total_days}} días de pre-notas
          </v-list-item-title>
          <v-list-item-subtitle>
            Del {{from_date}} al {{to_date}}
          </v-list-item-subtitle>
      </v-list-item>
      <v-divider></v-divider>
      <v-list-item prepend-icon="newspaper">
          <v-list-item-title class="_text-subtitle-1">
            {{ full_main.articles_count }} pre-notas ({{avg_per_day}} diarias)
          </v-list-item-title>
          <v-list-item-subtitle>
            Las notas extraídas de la fuente
          </v-list-item-subtitle>
      </v-list-item>
      <v-list-item>
        <template v-slot:prepend>
          <v-icon
            :color="ai_completed ? 'success' : 'warning'"
          >
            {{ ai_completed ? 'check_circle' : 'warning' }}
          </v-icon>
        </template>
        <v-list-item-title class="_text-subtitle-1">
          {{full_main.preclassified_count}} exploradas por la IA
        </v-list-item-title>
        <v-list-item-subtitle>
          Pre-notas que pasaron por el proceso vía IA
        </v-list-item-subtitle>
      </v-list-item>
      <v-list-item>
        <template v-slot:prepend>
          <v-icon
            :color="full_main.pending_count ? 'warning' : 'success'"
          >
            call_split
          </v-icon>
        </template>

        <v-list-item-title>
          {{ready_count}}/{{full_main.pre_selected}} clasificadas
        </v-list-item-title>
        <v-list-item-subtitle>
          De las {{full_main.pre_selected}} que fueron preseleccionadas,
          {{ready_count}} ya fueron clasificadas
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-col>
  <v-col
    v-if="full_main.articles_count > full_main.preclassified_count"
    cols="5"
    class="d-flex pa-0"
  >
    <div v-if="full_main.date_started">

      <span class="text-caption">
        Última actualización:
      </span>
      {{dayjs(full_main.date_started).fromNow()}}
    </div>
    <v-card-actions>
      <v-btn

        color="accent"
        variant="outlined"
        append-icon="replay"
        text="Ver pre-notas"
        @click="sendReprocess"
      >
        Volver a clasificar pre-notas
      </v-btn>
    </v-card-actions>
  </v-col>
</template>

<style scoped>

</style>