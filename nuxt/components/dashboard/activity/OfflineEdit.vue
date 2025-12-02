<script setup>
import { ref, computed } from 'vue'
import { useMainStore } from '~/store/index'
import { useRules } from '~/composables/useRules'
import UserSelect from "~/components/dashboard/custom_filters/UserSelect.vue";
import {storeToRefs} from "pinia";
import {useAuthStore} from "~/store/auth.js";
// import PersonDetail from '~/components/dashboard/common/PersonDetail.vue'

const authStore = useAuthStore()
const mainStore = useMainStore()
const { rules } = useRules()
const { cats } = storeToRefs(mainStore)
const OfflineForm = ref(null)

const dialog_add_offline = ref(false)
const offline_form = ref(false)
const day = ref(null)
const new_offline = ref({
  time_start: null,
  time_end: null,
  activity_type: null,
  name: null,
  users: [],
})

const offline_types = computed(() => cats.value.offline_types)
// const user = computed(() => mainStore.user_ocamis_details)
const { user_details_ocsa: user } = storeToRefs(authStore)

const offline_list = computed(() => {
  if (!offline_types.value) return []
  return Object.entries(offline_types.value).map(([key, value]) => {
    return { title: value, value: key }
  })
})

const need_name = computed(() => {
  return new_offline.value.activity_type === 'other' ||
    new_offline.value.activity_type === 'meeting'
})

function addOffline(dayData) {
  day.value = dayData
  dialog_add_offline.value = true
  new_offline.value = {
    time_start: '11:00:00',
    time_end: '13:00:00',
    activity_type: null,
    name: null,
    users: [user.value.id],
  }
}

function editOffline(offline) {
  dialog_add_offline.value = true
  new_offline.value = {
    ...offline,
    time_start: offline.date_start.format('HH:mm:ss'),
    time_end: offline.date_end.format('HH:mm:ss'),
  }
}

function closeDialog() {
  dialog_add_offline.value = false
}

async function saveOffline() {
  const { valid } = await OfflineForm.value.validate()
  if (valid) {
    const date_str = day.value.date.format('YYYY-MM-DD')
    const params = {
      ...new_offline.value,
      date_start: `${date_str} ${new_offline.value.time_start}`,
      date_end: `${date_str} ${new_offline.value.time_end}`,
    }
    await mainStore.saveOffline(params)
    OfflineForm.value.reset()
    dialog_add_offline.value = false
  }
}

defineExpose({
  addOffline,
  editOffline,
})
</script>

<template>
  <v-dialog
    v-model="dialog_add_offline"
    max-width="320"
  >
    <v-form
      ref="OfflineForm"
      v-model="offline_form"
    >
      <v-card>
        <v-card-title>
          Agregar actividad offline
        </v-card-title>
        <v-card-title
          v-if="day"
          class="text-h6 text-primary pt-0"
        >
          {{ day.date.format('DD-MMMM-YYYY') }} ({{ day.day_of_week }})
        </v-card-title>
        <v-card-text>
          <v-select
            v-model="new_offline.activity_type"
            :items="offline_list"
            item-title="title"
            item-value="value"
            label="Tipo de actividad"
            variant="outlined"
            :rules="[rules.required]"
          />
          <v-text-field
            v-if="need_name"
            v-model="new_offline.name"
            label="Nombre de la actividad"
            variant="outlined"
            :rules="[rules.required]"
          />
          <v-text-field
            v-model="new_offline.time_start"
            label="Hora de inicio"
            type="time"
            variant="outlined"
            :rules="[rules.required]"
          />
          <v-text-field
            v-model="new_offline.time_end"
            label="Hora de fin"
            type="time"
            variant="outlined"
            :rules="[rules.required]"
          />
          <UserSelect
            :final_filters="new_offline.users"
            field="users"
            is_filter
            style="max-width: 200px;"
            multiple
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="secondary"
            variant="text"
            @click="closeDialog"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="secondary"
            @click="saveOffline"
          >
            Agregar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>