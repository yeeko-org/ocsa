<script setup>

import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import Comments from "~/components/dashboard/utils/Comments.vue";

const props = defineProps({
  full_main: Object,
  final_collection_data: Object,
})

const rules = ref({
  required: value => !!value || "Campo requerido",
  defined: value => value !== undefined || "Debes seleccionar una opción",
})

function openLink(type) {
  if (type === 'icon')
    window.open('https://fonts.google.com/icons', '_blank')
    // window.open('https://material.io/resources/icons/?style=baseline', '_blank')
  else if (type === 'color')
    window.open('https://vuetifyjs.com/en/styles/colors/#material-colors', '_blank')
}

</script>

<template>
  <v-card-text
    class="d-flex flex-wrap"
  >
    <v-col cols="12" class="d-flex pa-0">
      <v-text-field
        v-if="final_collection_data.has.order"
        v-model="full_main.order"
        label="Orden"
        type="number"
        variant="outlined"
        class="mr-2"
        style="max-width: 70px;"
      >
      </v-text-field>
      <v-text-field
        v-if="final_collection_data.name_field"
        v-model="full_main[final_collection_data.name_field]"
        label="Nombre/Título"
        class="mr-2"
        variant="outlined"
        style="width: 300px;"
        :rules="[rules.required]"
      />
      <v-spacer></v-spacer>
      <template v-if="final_collection_data.status_groups">
        <StatusDetail
          v-for="status_group in final_collection_data.status_groups"
          :final_filters="full_main"
          :collection="status_group"
          style="max-width: 300px;"
          density="default"
          class="mr-1"
        />
      </template>
      <Comments
        v-if="final_collection_data.has.comments"
        :main="full_main"
        :final_collection_data="final_collection_data"
      />
    </v-col>
    <v-col
      v-if="final_collection_data.has.icon || final_collection_data.has.color"
      cols="12"
      class="d-flex pa-0"
    >
      <v-text-field
        v-if="final_collection_data.has.icon"
        v-model="full_main.icon"
        label="Ícono (material icons)"
        variant="outlined"
        style="max-width: 260px;"
        :rules="[rules.required]"
      >
        <template v-slot:append>
          <v-icon
            @click="openLink('icon')"
          >open_in_new</v-icon>
        </template>
      </v-text-field>
      <v-text-field
        v-if="final_collection_data.has.color"
        v-model="full_main.color"
        label="Color"
        variant="outlined"
        class="ml-6"
        style="max-width: 220px;"
        :rules="[rules.required]"
      >
        <template v-slot:append>
          <v-icon
            @click="openLink('color')"
          >open_in_new</v-icon>
        </template>
      </v-text-field>
    </v-col>
    <slot name="edit" :full_main="full_main">
      EDICIÓN 2 (REVISAR PORQUE NO ES NORMAL)
    </slot>
    <v-col
      v-if="final_collection_data.has.description
        && final_collection_data.name_field !== 'description'"
      cols="12"
      class="d-flex pa-0"
    >
      <v-textarea
        v-model="full_main.description"
        label="Descripción"
        rows="1"
        auto-grow
        class="mr-2"
        variant="outlined"
      ></v-textarea>
    </v-col>
    <v-col
      cols="12"
      class="d-flex pa-0"
    >
      <v-textarea
        v-if="final_collection_data.has.help_text"
        v-model="full_main.help_text"
        label="Texto visible de ayuda"
        variant="outlined"
        rows="2"
        auto-grow
        hint="Aparecerá una 'alerta' cuando se seleccione esta categoría"
        persistent-hint
        _hide-details
      >
      </v-textarea>
    </v-col>
  </v-card-text>
</template>

<style scoped>

</style>