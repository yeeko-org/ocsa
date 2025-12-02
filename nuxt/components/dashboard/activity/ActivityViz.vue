<script setup>
import { ref, computed } from 'vue'
import { useMainStore } from '~/store/index'
import * as d3 from 'd3'
import dayjs from 'dayjs'
import {storeToRefs} from "pinia"

const props = defineProps({
  day: {
    type: Object,
    required: true,
  },
  last_days: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['edit-offline'])

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const width = ref(window.innerWidth - 220)
const height = ref(50)
const tt_data = ref(null)
const posX = ref(-200)
const posY = ref(-200)
const is_tooltip = ref(false)

const activities_config = ref([
  {
    color: 'rgba(38,220,146,0.9)',
    field: 'offline',
    y: 0,
    stroke_width: 0,
    colors: {
      'weekly_meeting': 'rgba(34,208,113,0.9)',
      'meeting': 'rgba(38,220,156,0.9)',
      'training': 'rgba(41,190,150,0.9)',
      'pnt': 'rgba(21,162,41,0.9)',
      'other': 'rgba(16,128,83,0.9)',
    },
  },
  {
    color: 'rgba(203,49,200,0.93)',
    model_colors: {
      'article': 'rgba(203,49,200,0.93)',
      'note': 'rgba(82,49,203,0.93)',
      'project': 'rgb(11,49,138)',
      'location': 'rgb(4,72,61)',
    },
    field: 'click',
    y: 5,
    stroke_width: 0.5,
  },
  {
    color: 'rgba(66,18,183,0.6)',
    field: 'task',
    y: 10,
    stroke_width: 1,
  },
])

const offline_types = computed(() => cats.value.offline_types)

const start_hour = computed(() => dayjs('2000-01-01 04:50:00-06:00'))
const end_hour = computed(() => dayjs('2000-01-02 05:10:00-06:00'))

function drawChart() {
  const day = props.day
  const log = day.day_string === '30_11_2025' || day.day_string === '01_12_2025'
  if (log) {
    console.log('drawChart day', day)
  }
  const id = `day_${day.day_string}`
  const is_empty = d3.select(`#${id}`).empty()
  if (!is_empty) {
    d3.select(`#${id}`).select('svg').remove()
  }
  if (day.activities.length === 0) {
    return
  }
  const margin = { top: 5, right: 20, bottom: 18, left: 20 }
  const svg = d3.select(`#${id}`)
    .append('svg')
    .attr('width', width.value)
    .attr('height', height.value + margin.bottom)
    .attr('viewBox', [0, 0, width.value, height.value])

  const xScale = d3.scaleTime()
    .domain([start_hour.value, end_hour.value])
    .range([0, width.value])

  svg.append('g')
    .selectAll('rect.group')
    .data(day.groups)
    .join('rect')
    .attr('class', 'group')
    .attr('x', d => xScale(d.start_time))
    .attr('y', -5)
    .attr('height', height.value - 5)
    .attr('width', d => xScale(d.end_time) - xScale(d.start_time))
    .attr('fill', 'rgba(62,160,180,0.79)')
    .attr('opacity', 0.5)

  // if (log)
  //   console.log("activities_config", activities_config.value)

  activities_config.value.forEach((activity) => {
    const activity_data = day.activities.filter(d =>
      d.activity_type === activity.field)

    const rects = svg.append('g')
      .selectAll(`rect.${activity.field}`)
      .data(activity_data)
      .join('rect')
      .attr('class', activity.field)
      .attr('x', d => xScale(d.start_time))
      .attr('y', activity.y)
      .attr('height', 25)
      .attr('width', d => xScale(d.end_time) - xScale(d.start_time))
      .attr('fill', d => activity.colors
        ? activity.colors[d.offline_type]
        : activity.model_colors && d.model
          ? activity.model_colors[d.model]
          : activity.color
      )
      .attr('stroke', d =>  activity.colors
        ? activity.colors[d.offline_type]
        : activity.model_colors && d.model
          ? activity.model_colors[d.model]
          : activity.color
      )
      .attr('stroke-width', activity.stroke_width)

    if (activity.field === 'offline') {
      rects
        .attr('title', d => d.name || d.offline_type)
        .on('mouseover', function(ev, datum) {
          is_tooltip.value = true
          tt_data.value = datum
          posX.value = ev.clientX
          posY.value = ev.clientY
        })
        .on('mousemove', function(ev) {
          posX.value = ev.clientX
          posY.value = ev.clientY
        })
        .on('mouseout', function() {
          is_tooltip.value = false
        })
        .on('click', function(ev, datum) {
          emit('edit-offline', { day: props.day, datum })
        })
    }
  })
  const xAxis = g => g
    .attr('transform', `translate(0,${height.value - 10})`)
    .call(
      d3.axisBottom(xScale)
        .ticks(16)
        .tickFormat(d3.timeFormat('%H:%M'))
    )
  svg.append('g').call(xAxis)
}

defineExpose({
  drawChart,
})
</script>

<template>
  <div :id="`day_${day.day_string}`" class="position-relative">
    <div
      v-if="is_tooltip && tt_data"
      class="custom-tooltip"
      :style="{
        left: `${posX + 10}px`,
        top: `${posY + 10}px`,
      }"
    >
      <div class="font-weight-bold">
        {{ offline_types[tt_data.offline_type] }}
      </div>
      <div>{{ tt_data.name }}</div>
      <div>
        {{ tt_data.start_time.format('hh:mm a') }}
        - {{ tt_data.end_time.format('hh:mm a') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-tooltip {
  position: fixed;
  z-index: 1000;
  background-color: #0CA468;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  min-width: 180px;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>