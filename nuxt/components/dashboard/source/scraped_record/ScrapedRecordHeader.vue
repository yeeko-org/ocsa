<script setup>
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/utils/HeaderChip.vue";

dayjs.locale('es')

const props = defineProps({
  main: {
    type: Object,
    required: true,
  },
  show_details: Boolean,
  collection_data: Object,
})

const emits = defineEmits(['item-saved'])

const title = computed(() => {
  const format = 'DD MMM/YY'
  return `${dayjs(props.main.from_date).format(format)} -->
  ${dayjs(props.main.to_date).format(format)}`
})

const is_init_ready = computed(() => {
  return props.main.articles_count === props.main.analyzed_count
})

</script>
<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #title>
      <div class="d-flex flex-column align-start justify-start">
        <div class="text-caption text-purple-darken-1">
          {{main.source_full.name}}
        </div>
        <div class="font-weight-medium">
          {{ title }}
        </div>
      </div>
    </template>
    <template #details>
      <div class="d-flex flex-column align-center">
        <span
          class="text-caption text-grey"
        >
          Recolección:
        </span>
        <v-chip
          v-if="!is_init_ready"
          :color="main.errors_count > 0 ? 'red-darken-1' : 'orange-darken-3'"
        >

          <span v-if="main.errors_count > 0">
            Con errores
          </span>
          <span v-else class="ml-1">
            Reclasificar
          </span>
        </v-chip>
        <v-chip
          v-else
          color="success"
        >
          Exitosa
          {{main.errors_count ? '⚠️' : '✅'}}

        </v-chip>
      </div>
      <HeaderChip
        :count="main.articles_count"
        collection_name="article"
        class="ml-2"
        icon="article"
        color="purple-darken-4"
        width="57"
      />
      <HeaderChip
        :count="main.scraped_count"
        class="ml-2"
        label="Scrapeado"
        label_plural="Scrapeados"
        color="indigo"
        icon="document_scanner"
        width="57"
      />
      <HeaderChip
        :count="main.analyzed_count"
        class="ml-2"
        label="Preclasificado por IA"
        label_plural="Preclasificados por IA"
        color="blue-darken-2"
        icon="assistant"
        width="57"
      />
      <HeaderChip
        :count="main.first_pre_selected_count"
        class="ml-2"
        label="Pre-seleccionado por IA"
        label_plural="Pre-seleccionados por IA"
        icon="fact_check"
        color="light-blue"
        width="49"
      />
      <HeaderChip
        :count="main.pre_filtered_count"
        class="ml-2"
        label="Re-analizado por IA"
        label_plural="Re-analizados por IA"
        icon="auto_mode"
        color="cyan-darken-1"
        width="49"
      />
      <HeaderChip
        :count="main.pending_count"
        class="ml-2"
        label="Pendiente"
        label_plural="Pendientes"
        icon="hourglass_empty"
        :color="main.pending_count ? 'orange' : 'green'"
        is_reverse
        :tooltip_complement="`<b> ${main.ready_count} </b> Clasificados`"
      />

    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>