<script setup>
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";
import UserSelect from "~/components/dashboard/custom_filters/UserSelect.vue";
const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

const emits = defineEmits(['item-saved'])

// const addMention = () => {
//   console.log("add mention")
//   if (!props.full_main.mentions) {
//     props.full_main.mentions = []
//   }
//   props.full_main.mentions.push({})
// }

</script>

<template>
  <div v-if="false" class="d-flex" style="width: 100%;">
    <v-textarea

      v-model="full_main.title"
      label="Título de la nota"
      variant="outlined"
      rows="1"
      auto-grow
      _style="width: 100%;"
    >
    </v-textarea>
  </div>
  <div class="d-flex" style="width: 100%;">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="source_types"
      :width="160"
    />
    <SelectDate
      :init_date="full_main.date"
      @update-date="full_main.date = $event"
    />
    <v-textarea
      v-model="full_main.subtitle"
      label="Subtítulo de la pre-nota"
      variant="outlined"
      class="ml-2"
      rows="2"
      max-rows="3"
      auto-grow
      max-width="500px"
    >
    </v-textarea>
    <v-text-field
      v-model="full_main.section"
      label="Sección"
      variant="outlined"
      class="ml-2"
      style="max-width: 200px;"
    >
    </v-text-field>
  </div>
  <div class="d-flex" style="width: 100%;">
    <v-text-field
      v-model="full_main.author"
      label="Autor"
      variant="outlined"
      class="ml-2"
      style="width: 240px;"
    >
    </v-text-field>
    <v-text-field
      v-model="full_main.pages"
      label="Páginas"
      variant="outlined"
      class="ml-2"
      style="width: 80px;"
    >
    </v-text-field>
    <v-text-field
      v-model="full_main.capture_date"
      label="Fecha de captura"
      variant="plain"
      readonly
      class="ml-3"
      style="width: 100px;"
    >
    </v-text-field>
    <UserSelect
      :final_filters="full_main"
      field="editors"
      label="Editores"
      readonly
      multiple
      chips
    />
    <UserSelect
      :final_filters="full_main"
      field="reviewers"
      label="Revisores"
      class="ml-3"
      color="secondary"
      readonly
      multiple
      chips
    />
  </div>
  <v-text-field
    v-model="full_main.link"
    label="Enlace a la nota"
    variant="outlined"
    class="mr-2"
    style="width: 600px;"
  >
    <template #append v-if="full_main.link">
      <v-btn
        color="accent"
        variant="outlined"
        icon="open_in_new"
        :href="full_main.link"
        target="_blank"
        v-tooltip:bottom="'Abrir enlace'"
      ></v-btn>
    </template>
  </v-text-field>
</template>

<style scoped>

</style>