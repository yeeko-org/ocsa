<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import dayjs from 'dayjs'

// Props
const props = defineProps({
  init_date: {
    type: [String, Date, Object],
    required: false,
  },
  is_req: {
    type: Boolean,
    required: false,
    default: false,
  },
  label: {
    type: String,
    required: false,
    default: 'Fecha',
  },
  hint: {
    type: String,
    required: false,
    default: null,
  },
  persistent_hint: {
    type: Boolean,
    required: false,
    default: false,
  },
})

// Emits
const emits = defineEmits(['update-date'])

// Reactive data
const showMenuDate = ref(false)
const rules = {
  required: (value) => !!value || 'Este campo no puede quedar vacío.',
}

// Reactive real_date to emit updated values
const realDate = ref(props.init_date)

// Computed property for formatted date
const computedDateFormatted = computed({
  get() {
    console.log('computedDateFormatted')
    return formatDate(props.init_date)
    // const finalDate = realDate.value || props.init_date
    // return dayjs(finalDate).format('DD/MM/YYYY')
  },
  set(newDate) {
    // Convert to 'YYYY-MM-DD' format and emit
    console.log('newDate', newDate)
    realDate.value = dayjs(newDate).format('YYYY-MM-DD')
    emits('update-date', realDate.value)
  },
})

// Methods for formatting and parsing date
const formatDate = (date) => {
  if (!date) return null
  const parsedDate = dayjs(date)
  return parsedDate.isValid() ? parsedDate.format('DD/MM/YYYY') : null
}

const parseDate = (date) => {
  if (!date) return null
  const [day, month, year] = date.split('/')
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}

// Watcher to reactively update realDate based on init_date prop changes
watch(() => props.init_date, (newVal) => {
  realDate.value = newVal
})

function saveDate() {
  console.log('saveDate')
  realDate.value = parseDate(computedDateFormatted.value)
  emits('update-date', realDate.value)
  showMenuDate.value = false
}

</script>

<template>
  <v-menu
    v-model="showMenuDate"
    :nudge-right="40"
    :close-on-content-click="false"
    transition="scale-transition"
    min-width="290px"
    offset-y
  >
    <template v-slot:activator="{ props }">
      <v-text-field
        v-model="computedDateFormatted"
        :label="label"
        variant="outlined"
        :rules="[is_req ? rules.required : true]"
        v-bind="props"
        class="px-3"
        :hint="hint"
        :persistent-hint="persistent_hint"
        style="max-width: 400px"
        @blur="realDate.value = parseDate(computedDateFormatted)"
      ></v-text-field>
    </template>

    <v-date-picker
      color="accent"
      v-model="realDate"
      show-adjacent-months
      rounded="lg"
      cancel-text="Cancelar"
      ok-text="Guardar"
      title="Selecciona una fecha"
      @click:save="showMenuDate = false"
      @click:cancel="showMenuDate = false"
    >
      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          color="accent"
          @click="showMenuDate = false"
        >
          Cancelar
        </v-btn>
        <v-btn
          variant="outlined"
          color="accent"
          @click="saveDate"
        >
          Guardar
        </v-btn>
      </template>
    </v-date-picker>
  </v-menu>
</template>
