<script setup>
import PanelList from "~/components/dashboard/common/main/PanelList.vue";
import { useMainStore } from "~/store/index.js";
import { storeToRefs } from "pinia";
import CalendarDisplay from "~/components/dashboard/source/CalendarDisplay.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";
import dayjs from 'dayjs'

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { saveSimple, getSimple, fetchElements } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  }
})

const loading = ref(false)
const result_articles = ref([])
const recordForm = ref(null)
const errors = ref(null)

const new_record = ref({
  when: null,
  from_date: null,
  to_date: null,
})

const selected_year = ref(null)
const year_scraped_records = ref([])
const loading_year = ref(false)

const scraped_record_collection = computed(() => {
  return schemas.value.collections_dict['scraped_record']
})

const years = computed(() => {
  const first_year = 2020
  const current_year = dayjs().year()
  const result = []
  for (let y = first_year; y <= current_year; y++) {
    result.push(y)
  }
  return result
})

const year_scraped_records_with_source = computed(() => {
  const source_full = { id: props.full_main.id, name: props.full_main.name }
  return year_scraped_records.value.map(scraped_record => ({
    ...scraped_record,
    source_full,
  }))
})

async function selectYear(year) {
  selected_year.value = year
  loading_year.value = true
  year_scraped_records.value = []
  const result = await fetchElements(['scraped_record', {
    from_date: `${year}-01-01`,
    to_date: `${year}-12-31`,
    source: props.full_main.id,
  }])
  year_scraped_records.value = result.results || []
  loading_year.value = false
}

const new_scraped_records = ref([])

async function saveScrapedRecord() {
  const { valid } = await recordForm.value.validate()
  if (!valid) return

  loading.value = true
  errors.value = null
  result_articles.value = []
  const data = {
    from_date: new_record.value.from_date,
    to_date: new_record.value.to_date,
    source: props.full_main.id,
  }
  saveSimple(['scraped_date', data]).then(response => {
    // console.log("response saveScrapedRecord", response)
    if (response.errors?.length > 0) {
      loading.value = false
      errors.value = response.errors
      return
    }
    loading.value = false
    new_record.value.from_date = null
    new_record.value.to_date = null
    new_scraped_records.value.push(response.scraped_record)
  })
}

const loading_new_records = ref(false)
async function reloadNewScrapedRecords() {
  loading_new_records.value = true
  const responses = await Promise.all(
    new_scraped_records.value.map(scraped_record => {
      return getSimple(['scraped_record', scraped_record.id])
    })
  )
  // console.log("responses", responses)
  loading_new_records.value = false
}

function updateDate(date, field) {
  if (field === 'from_date') {
    new_record.value.from_date = date
  } else if (field === 'to_date') {
    new_record.value.to_date = date
  }
}

function selectDay(day) {
  if (new_record.value.from_date && new_record.value.to_date) {
    new_record.value.from_date = day.full_day
    new_record.value.to_date = null
  }
  else if (new_record.value.from_date && !new_record.value.to_date) {
    new_record.value.to_date = day.full_day
  } else {
    new_record.value.from_date = day.full_day
    new_record.value.to_date = null
  }
}


</script>

<template>
  <v-card class="mb-4 pa-3">
    <div class="d-flex align-end justify-start mb-4">
      <div>
        <v-card-subtitle>
          Selecciona un año para ver los periodos extraídos de noticias:
        </v-card-subtitle>
        <div class="d-flex flex-wrap align-center">
          <v-btn
            v-for="year in years"
            :key="year"
            :color="selected_year === year ? 'primary' : 'default'"
            variant="outlined"

            class="mr-1 mb-1"
            :loading="loading_year && selected_year === year"
            @click="selectYear(year)"
          >
            {{ year }}
          </v-btn>
        </div>
      </div>
      <v-spacer></v-spacer>
      <v-card
        class="ml-4 pa-2"
        style="width: 460px;"
        color="grey-lighten-3"
      >
        <span class="ml-3">
          Periodos extraídos de noticias:
        </span>
        <v-form
          ref="recordForm"
          class="d-flex align-center"
        >
          <v-col cols="12" class="d-flex">
            <SelectDate
              :init_date="new_record.from_date"
              label="Desde"
              class="mr-2"
              @update-date="updateDate($event, 'from_date')"
              required
              view_mode="months"
              clearable
            />
            <SelectDate
              :init_date="new_record.to_date"
              label="Hasta"
              class="mr-2"
              @update-date="new_record.to_date = $event"
              required
              clearable
            />

            <v-btn
              color="accent"
              variant="elevated"
              class="ml-4"
              @click="saveScrapedRecord()"
              :loading="loading"
            >
              Traer periodo
            </v-btn>
          </v-col>
          <v-col cols="12" v-if="false">
            Hola info
          </v-col>
        </v-form>
      </v-card>
    </div>
    <v-alert
      v-if="errors"
      type="error"
      class="mb-4"
      dense
      outlined
    >
      {{errors}}
    </v-alert>
    <CalendarDisplay
      v-if="selected_year"
      :scraped_records="year_scraped_records"
      :new_record="new_record"
      :year="selected_year"
      @select-day="selectDay($event)"
    />
    <template
      v-if="new_scraped_records.length > 0"
    >
      <v-card-title
        class="px-0 mt-2 d-flex"
      >
        Nuevas consultas enviadas:
         <v-btn
           color="accent"
           variant="outlined"
           size="x-small"
           icon
           class="ml-4"
           :loading="loading_new_records"
           @click="reloadNewScrapedRecords()"
         >
           <v-icon>
             cached
           </v-icon>
         </v-btn>
      </v-card-title>
      <v-card-text class="px-0">
        <PanelList
          :results="new_scraped_records"
          :collection_data="scraped_record_collection"
        />
      </v-card-text>
    </template>
    <template v-if="selected_year">
      <v-card-title
        v-if="year_scraped_records.length"
        class="px-0 mt-2"
      >
        Consultas realizadas en {{ selected_year }}:
      </v-card-title>
      <v-card-text class="px-0">
        <PanelList
          :results="year_scraped_records_with_source"
          :collection_data="scraped_record_collection"
        />
      </v-card-text>
    </template>
  </v-card>
</template>

<style scoped>

</style>
