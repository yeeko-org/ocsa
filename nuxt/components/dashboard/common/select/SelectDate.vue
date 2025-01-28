<script setup>

import dayjs from "dayjs";

const props = defineProps({
  init_date: {
    type: String,
    required: false,
  },
  label: {
    type: String,
    required: false,
    default: 'Fecha de la nota',
  },
  disabled: Boolean,
  hide_details: Boolean,
  is_filter: Boolean,
  max_width: {
    type: String,
    default: '180px',
  },
})

const show_menu_date = ref(false)
const emits = defineEmits(['update-date'])

const human_date = computed(() => {
  if (!props.init_date) return ''
  return dayjs(props.init_date).format('DD/MM/YYYY')
})

const getDate = computed(() => {
  if (!props.init_date) return new Date()
  return dayjs(props.init_date).toDate()
})

function editDate(date) {
  console.log("edit date", date)
  // props.full_main.date = dayjs(date).format('YYYY-MM-DD')
  let new_date = null
  if (date)
    new_date = dayjs(date).format('YYYY-MM-DD')
  emits('update-date', new_date)
  show_menu_date.value = false
}

</script>

<template>
  <v-menu
    v-model="show_menu_date"
    :nudge-right="40"
    :close-on-content-click="false"
    transition="scale-transition"
    min-width="290px"
    offset-y
  >
    <template v-slot:activator="{ props }">
      <v-text-field
        v-bind="props"
        :model-value="human_date"
        readonly
        :label="label"
        :variant="is_filter ? 'underlined' : 'outlined'"
        class="ml-2"
        :style="`max-width: ${max_width}`"
        :hide-details="is_filter"
        :clearable="is_filter"
        :density="is_filter ? 'compact' : 'default'"
        clear-icon="close"
        @click:clear="editDate(null)"
      >
      </v-text-field>
    </template>
    <v-date-picker
      :modelValue="getDate"
      @update:modelValue="editDate"
      color="accent"
      show-adjacent-months
      cancel-text="Cancelar"
      ok-text="Guardar"
      title="Selecciona una fecha"
      :disabled="disabled"
    >
    </v-date-picker>
  </v-menu>
</template>

<style scoped>

</style>