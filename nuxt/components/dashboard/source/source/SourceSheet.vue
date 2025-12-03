<script setup>
import PanelList from "~/components/dashboard/common/PanelList.vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import CalendarDisplay from "~/components/dashboard/source/CalendarDisplay.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { saveSimple } = mainStore
import dayjs from 'dayjs'

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
const months_ago = ref(30)
const errors = ref(null)

const new_record = ref({
  when: null,
  from_date: null,
  to_date: null,
})

const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})
const scraped_record_collection = computed(() => {
  return schemas.value.collections_dict['scraped_record']
})

const scraped_records = computed(() => {
  const source_full = {'id': props.full_main.id, 'name': props.full_main.name}
  return props.full_main.scraped_records.map(scraped_record => {
    scraped_record.source_full = source_full
    return scraped_record
  })
})

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
    if (response.errors) {
      loading.value = false
      errors.value = response.errors
      return
    }
    loading.value = false
    new_record.value.from_date = null
    new_record.value.to_date = null
    props.full_main.scraped_records.push(response.scraped_record)
  })
}

function updateDate(date, field) {
  if (field === 'from_date') {
    new_record.value.from_date = date
    // if (!new_record.value.to_date) {
    //   // add 30 days to from_date
    //   let after_30_days = dayjs(date).add(30, 'day').toDate()
    //   after_30_days = dayjs(after_30_days).format('YYYY-MM-DD')
    //   new_record.value.to_date = after_30_days
    // }
  } else if (field === 'to_date') {
    new_record.value.to_date = date
  }
}

function selectDay(day) {
  // console.log("selectDay", day)
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
  // if (!day.limit)
  //   return
}


</script>

<template>
  <v-card class="mb-4 pa-3">
    <div class="d-flex align-end justify-start mb-4">
      <v-card
        class="align-center pl-3 d-flex"
        variant="flat"
        style="width: 240px;"
      >
        <v-text-field
          v-model="months_ago"
          label="Meses atrás"
          variant="outlined"
          class="mt-2"
          density="compact"
          style="max-width: 120px;"
          type="number"
          hide-details
        >
        </v-text-field>
      </v-card>
      <v-spacer></v-spacer>
      <v-card
        class="ml-4 pa-2"
        style="width: 600px;"
        color="grey-lighten-3"
      >
        Periodos extraídos de noticias:
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
            <v-spacer></v-spacer>
            <v-btn
              color="accent"
              variant="elevated"
              @click="saveScrapedRecord()"
              :loading="loading"
            >
              Traer periodo
            </v-btn>
          </v-col>
          <v-col cols="12">
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
      :scraped_records="full_main.scraped_records"
      :new_record="new_record"
      :months_ago="months_ago"
      @select-day="selectDay($event)"
    />
    <v-card-title
      v-if="full_main.scraped_records?.length"
      class="px-0 mt-2"
    >
      Consultas realizadas:
    </v-card-title>
    <v-card-text class="px-0">
      <PanelList
        :results="scraped_records"
        :collection_data="scraped_record_collection"
        :show_details="true"
      />
    </v-card-text>

<!--    <PanelList-->
<!--      v-if="full_main.note"-->
<!--      :results="[full_main.note]"-->
<!--      :collection_data="note_collection"-->
<!--      :show_details="true"-->
<!--    />-->
  </v-card>
</template>

<style scoped>

</style>