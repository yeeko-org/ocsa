<script setup>

import dayjs from 'dayjs'
// add isBetween plugin
import isBetween from 'dayjs/plugin/isBetween'
dayjs.extend(isBetween)
import 'dayjs/locale/es'
dayjs.locale('es')

const props = defineProps({
  scraped_records: Array,
  new_record: Object,
  months_ago: {
    type: Number,
    default: 30
  }
})

const emits = defineEmits(['select-day'])
const is_ready = ref(false)

function getLimits() {
  if (!props.scraped_records)
    return {}
  // sort apply queries by "has_errors"
  props.scraped_records.sort((a, b) => {
    return a.has_errors - b.has_errors
  })
  return props.scraped_records.reduce((acc, record) => {
    let base_limit = {has_errors: record.has_errors}
    if (record.from_date === record.to_date)
      acc[record.from_date] = {
        ...base_limit, icon: 'sync_alt', location: 'top left'}
    else{
      acc[record.from_date] = {
        ...base_limit, icon: 'play_arrow', location: 'top left'}
      acc[record.to_date] = {
        ...base_limit, icon: 'arrow_back_ios', location: 'top right'}
    }
    return acc
  }, {})
}

function getLimitsWithDayJS() {
  if (!props.scraped_records)
    return {}
  props.scraped_records.sort((a, b) => {
    return a.has_errors - b.has_errors
  })
  return props.scraped_records.map(record => {
    return {
      from_date: dayjs(record.from_date),
      to_date: dayjs(record.to_date),
      has_errors: record.has_errors,
      color: record.has_errors ? 'orange' : 'cyan'
    }
  })
}

const recent_months_with_day_js = computed(() => {
  if (is_ready.value)
    return
  const now = dayjs()
  const real_months_ago = now.subtract(props.months_ago, 'month')
  let current_day = real_months_ago.startOf('month')
  current_day = current_day.subtract(1, 'day')
  let all_months = {}
  const limits = getLimits()
  let between_dates = getLimitsWithDayJS()
  if (props.new_record && props.new_record.from_date){
    const from_date = dayjs(props.new_record.from_date)
    let to_date = null
    if (props.new_record.to_date)
      to_date = dayjs(props.new_record.to_date)
    else
      to_date = from_date
    between_dates.push({
      from_date: from_date,
      to_date: to_date,
      has_errors: false,
      color: 'green-lighten-2'
    })
  }
  while (current_day.isBefore(now)){
    current_day = current_day.add(1, 'day')
    const year_month = current_day.format('YYYY-MM')
    const date_str = current_day.format('YYYY-MM-DD')
    const limit = limits[date_str]
    const is_between = between_dates.find(date => {
      if (current_day.isBetween(date.from_date, date.to_date, null, '[]'))
        return date
    })

    const day_obj = {
      number: current_day.date(),
      month: current_day.month() + 1,
      year: current_day.year(),
      full_day: date_str,
      date: current_day.toDate(),
      limit: limit,
      is_between: is_between
    }
    if (all_months[year_month])
      all_months[year_month].push(day_obj)
    else
      all_months[year_month] = [day_obj]
  }
  // console.log("all_months", all_months)
  return Object.entries(all_months).map(([month, days]) => {
    const month_str = dayjs(month).format('MMM')
    const year = days[0].year % 1000
    return {"month": month_str, "days": days, year: year}
  })

})

function indirectSelectDay(day) {
  // const date = dayjs(day.full_day)
  emits('select-day', {
    date: day.date,
    limit: day.limit,
    is_between: day.is_between,
    full_day: day.full_day,
  })
}

</script>

<template>
  <v-card
    class="pa-2"
    color="grey-lighten-4"
    style="width: 100%;"
  >
    <div
      v-for="month in recent_months_with_day_js"
      :key="month.month"
      class="d-flex align-center"
      :class="month.month === 'ene' ? 'mt-4' : ''"
    >
      <div
        class="text-subtitle-1 mr-3 text-left"
        style="width: 60px;"
      >
        {{month.month}}
        <span class="text-grey-darken-1">
          {{month.year}}
        </span>
      </div>
      <div
        v-for="day in month.days"
        :key="day.full_day"
      >
        <v-badge
          v-if="day.limit"
          color="transparent"
          variant="text"
          offset-x="5"
          :location="day.limit.location"
        >
          <template v-slot:badge>
            <v-icon
              :color="day.limit.has_errors ? 'red' : 'purple'"
              size="18"
            >
              {{day.limit.icon}}
            </v-icon>
          </template>
          <v-avatar
            :color="day.is_between?.color || 'cyan-lighten-4'"
            size="x-small"
            class="mr-1 text-caption text-grey-darken-3"
          >
            {{day.number}}
          </v-avatar>
        </v-badge>
        <v-avatar
          v-else
          :color="day.is_between?.color || 'cyan-lighten-4'"
          size="x-small"
          class="mr-1 text-caption text-grey-darken-2 cursor-pointer"
          @click="indirectSelectDay(day)"
        >
          {{day.number}}
        </v-avatar>
      </div>
    </div>
  </v-card>

</template>

<style scoped>
.turn180 {
  transform: rotate(180deg);
}
</style>