<script setup>

import DescriptionIcon from "~/components/dashboard/common/utils/DescriptionIcon.vue";
import ParagraphFilter from "~/components/dashboard/capture/ParagraphFilter.vue";

const props = defineProps({
  locations: {
    type: Array,
    required: true,
  },
  can_edit_pre_save: {
    type: Boolean,
    default: true,
  },
  note_id: Number,
})

const emits = defineEmits(['discard-location'])

const show_discarded = ref(false)

const pre_locations = computed(() => {
  return props.locations.filter(loc => loc.path)
})

const final_locations = computed(() => {
  if (show_discarded.value)
    return pre_locations.value
  return pre_locations.value.filter(loc => !loc.discarded)
})

const discarded_count = computed(() => {
  return pre_locations.value.filter(loc => loc.discarded).length
})

</script>

<template>
  <v-card
    v-if="final_locations.length > 0"
    variant="tonal"
    color="indigo-accent-2"
    class="text-body-2 px-2 py-1 mt-2"
  >
    <div
      v-for="location in final_locations"
      :key="location.id"
      class="d-flex align-center ga-1 w-100"
    >
      <v-icon
        size="20"
        color="indigo-accent-2"
        class="mr-2"
      >
        location_on
      </v-icon>
      <b>{{location.state_str}}</b>
      <span v-if="location.municipality_text">
        - {{location.municipality_text}}
      </span>
      <span v-if="location.locality_text">
        ({{location.locality_text}})
      </span>
      <DescriptionIcon
        :description="location.details"
        size="x-small"
        icon_size="large"
      />
      <v-spacer> </v-spacer>
      <ParagraphFilter
        :paragraphs="location?.paragraphs"
        :note_id="note_id"
        :path="location?.path"
        btn_size="30"
      />

      <v-btn
        v-if="!location.discarded"
        color="success"
        icon
        variant="outlined"
        size="30"
        v-tooltip="'Ubicación retomada'"
        :disabled="!can_edit_pre_save"
        @click="emits('discard-location', location)"
      >
        <v-icon
          size="20"
        >
          done
        </v-icon>
      </v-btn>
    </div>
    <div
      v-if="discarded_count > 0 && !show_discarded"
      class="text-center mt-2"
    >
      <v-btn
        text
        size="small"
        @click="show_discarded = true"
      >
        Mostrar ubicaciones retomadas ({{discarded_count}})
      </v-btn>
    </div>
  </v-card>

</template>

<style scoped>

</style>
