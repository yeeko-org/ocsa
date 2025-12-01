<script setup>
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

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
      <v-chip
        v-if="main.errors && main.errors.length > 0"
        color="error"
        class="ml-3"
      >
        Tiene errores
      </v-chip>
      <v-chip
        v-else
        color="success"
        class="ml-3"
      >
        Exitoso
      </v-chip>
      <HeaderChip
        :count="main.articles_count"
        collection_name="article"
        class="ml-2"
        horizontal
      />
      <HeaderChip
        :count="main.preclassified_count"
        class="ml-2"
        label="Preclasificados"
        label_plural="Preclasificados"
        collection_name="article"
        color="light-blue"
        icon="smart_toy"
      />
      <HeaderChip
        :count="main.pending_count"
        class="ml-2"
        label="Pendiente"
        label_plural="Pendientes"
        icon="hourglass_empty"
        :color="main.pending_count ? 'orange' : 'green'"
        is_reverse
        :tooltip_complement="`De <b>${main.pre_selected}</b> pre-seleccionados`"
      />

    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>