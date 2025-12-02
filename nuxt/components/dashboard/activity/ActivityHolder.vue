<script setup>
import { nextTick } from 'vue'
import {storeToRefs} from "pinia";
import { useMainStore } from '~/store/index'
import {useAuthStore} from '~/store/auth.js'
import { useDates } from '~/composables/useDates'
import * as d3 from 'd3'
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import ActivityViz from '~/components/dashboard/activity/ActivityViz.vue'
import UserSelect from "~/components/dashboard/custom_filters/UserSelect.vue";
import OfflineEdit from '~/components/dashboard/activity/OfflineEdit.vue'

dayjs.locale('es')

const mainStore = useMainStore()
const authStore = useAuthStore()
const { months_of_year } = useDates()

const activity_viz_refs = ref([])
const offline_create = ref(null)

const first_day = ref('2000-01-01')
const menu = ref(false)
const loading = ref(false)
const filters = ref({
  days_ago: 60,
  user: null,
})
const last_days = ref([])

const {
  activities,
  spend_groups,
  cats_ready
} = storeToRefs(mainStore)
const { user_details_ocsa: user } = storeToRefs(authStore)

const disabled_person = computed(() =>
  !user.value?.is_superuser
)

const width = computed(() => window.innerWidth - 160)

// function setActivityVizRef(el, index) {
//   if (el) {
//     activity_viz_refs.value[index] = el
//   }
// }

function getActivities() {
  loading.value = true
  mainStore.fetchActivities(filters.value).then(() => {
    getLastDays()
    nextTick(() => {
      console.log('activity_viz_refs', activity_viz_refs.value)
      activity_viz_refs.value.forEach((vizRef) => {
        if (vizRef && vizRef.drawChart) {
          vizRef.drawChart()
        }
      })
      if (!filters.value.user)
        filters.value.user = user.value.id
      loading.value = false
    })
  })
}

function getDays(days = 60) {
  let dates = {}
  for (let i = 0; i < days + 1; i++) {
    let date = new Date()
    date.setDate(date.getDate() - i)
    let day = dayjs(date).format('DD/MM/YYYY')
    const month = months_of_year[date.getMonth()]
    const day_str = dayjs(date).format('D')
    let day_of_week = dayjs(date).format('dddd')
    dates[day] = {
      activities: [],
      groups: [],
      date: dayjs(date).startOf('day'),
      day: day,
      day_of_week: day_of_week,
      is_sunday: day_of_week === 'domingo',
      human_day: `${day_str}-${month.short_name}`,
      human_month: dayjs(date).format('MMMM'),
      day_string: dayjs(date).format('DD_MM_YYYY'),
      week_hours: 0,
      hours: 0,
    }
  }
  return dates
}

function getLastDays() {
  let dates = getDays(filters.value.days_ago)
  activities.value.forEach((activity) => {
    const start = dayjs(activity.date_start)
    const dayVal = start.hour() < 6 ? '2000-01-02' : '2000-01-01'
    activity.start_time = dayjs(start.format(`${dayVal} HH:mm:ss`))
    const end = activity.date_end
      ? dayjs(activity.date_end)
      : start.add(1, 'second')
    activity.end_time = dayjs(end.format(`${dayVal} HH:mm:ss`))
    activity.duration = end.diff(start, 'seconds')
    const start_minus = start.subtract(5, 'hours')
    const date_start = start_minus.format('DD/MM/YYYY')
    if (dates[date_start]) {
      dates[date_start].activities.push(activity)
    }
  })
  spend_groups.value.forEach((group) => {
    const start = dayjs(group.start)
    const dayVal = start.hour() < 6 ? '2000-01-02' : '2000-01-01'
    group.start_time = dayjs(start.format(`${dayVal} HH:mm:ss`))
    const end = dayjs(group.end)
    group.end_time = dayjs(end.format(`${dayVal} HH:mm:ss`))
    const start_minus = start.subtract(5, 'hours')
    const date_start = start_minus.format('DD/MM/YYYY')
    if (dates[date_start]) {
      dates[date_start].groups.push(group)
    }
  })
  let days = Object.values(dates)
  days = days.reverse()
  let last_week = 0.0
  days = days.map((day) => {
    let groups = day.groups
    const sum_seconds = d3.sum(groups, d => d.seconds)
    const hours = sum_seconds / 3600
    last_week += hours
    if (day.is_sunday) {
      day.week_hours = last_week
      last_week = 0
    }
    day.hours = hours
    return day
  })
  days[days.length - 1].week_hours = last_week
  days[days.length - 1].is_sunday = true
  days = days.reverse()
  last_days.value = days
}

function addOffline(day) {
  offline_create.value?.addOffline(day)
}

function editOffline(data) {
  offline_create.value?.addOffline(data.day)
}

onMounted(() => {
  getActivities()
})
</script>

<template>
  <v-card class="px-3" elevation="10" height="100%">
    <v-card-title class="d-flex align-center flex-wrap">
      Actividades
      <v-text-field
        v-model="filters.days_ago"
        label="Días atrás"
        type="number"
        hide-details
        density="compact"
        class="ml-6"
        style="max-width: 80px;"
        @keyup.enter="getActivities"
      />
      <UserSelect
        v-if="cats_ready"
        :final_filters="filters"
        field="user"
        is_filter
        style="max-width: 20px;"
        :disable="disabled_person"
        class="ml-3"
        @update:model-value="getActivities"
      />
      <v-btn
        color="primary"
        variant="outlined"
        class="ml-3"
        @click="getActivities"
      >
        Obtener
      </v-btn>
    </v-card-title>
    <v-row v-if="loading" class="pa-3">
      <v-progress-linear
        indeterminate
        color="primary"
        height="10"
      />
    </v-row>
    <v-card
      v-for="(day, index) in last_days"
      :key="day.day_string"
      variant="outlined"
      class="pl-2"
      :class="day.is_sunday ? 'mt-3' : ''"
    >
      <v-col
        v-if="day.is_sunday"
        cols="12"
        class="text-subtitle-1 font-weight-bold py-2"
      >
        Semana {{ day.human_month }}
        <span class="text-primary font-weight-bold">
          {{ day.week_hours.toFixed(2) }} hrs
        </span>
      </v-col>
      <v-row>
        <v-col
          class="flex-grow-0"
          style="min-width: 104px; max-width: 104px;"
        >
          <div>
            <div
              class="d-flex align-center text-subtitle-1
                font-weight-bold pt-1"
              style="max-height: 18px; min-width: 96px;"
            >
              {{ day.human_day }}
              <v-btn
                color="secondary"
                icon
                size="small"
                variant="text"
                @click="addOffline(day)"
              >
                <v-icon size="small">add</v-icon>
              </v-btn>
            </div>
            <div class="text-caption">
              {{ day.day_of_week }}
            </div>
          </div>
          <div
            v-if="day.hours > 0"
            class="text-body-2 text-primary font-weight-bold"
          >
            {{ day.hours.toFixed(2) }} hrs
          </div>
        </v-col>
        <v-col class="flex-grow-1">
          <ActivityViz
            ref="activity_viz_refs"
            :day="day"
            :last_days="last_days"
            @edit-offline="editOffline"
          />
        </v-col>
      </v-row>
    </v-card>
    <OfflineEdit ref="offline_create" />
  </v-card>
</template>