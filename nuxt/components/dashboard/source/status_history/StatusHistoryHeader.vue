<script setup>
import dayjs from 'dayjs'
import 'dayjs/locale/es'
dayjs.locale('es')

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import TitleCommon from "~/components/dashboard/generic/TitleCommon.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
const props = defineProps({
  main: {
    type: Object,
    required: true,
  },
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
    :width="380"
  >

    <template #title>
      <div class="d-flex flex-column align-center">
        <div class="text-caption text-grey-darken-1">

          <span v-if="main.date">
            {{dayjs(main.date).format('DD/MM/YYYY')}}
          </span>
          <span v-else>
            Sin fecha
          </span>
        </div>

        <v-card
          color="purple"
          rounded="lg"
          variant="outlined"
          class="mx-2 d-flex flex-column"
        >
          <SelectGroup
            :main_object="main"
            filter_group_name="status_projects"
            main_collection_name="status_history"
            :width="160"
            is_display
          />
        </v-card>
      </div>
      <ExtractivismIcons
        :project="main.project_full"
      />
      <TitleCommon
        :title_text="main.project_full?.name"
        :title_width="260"
        card_class="ml-2 text-body-1"
      />

    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>