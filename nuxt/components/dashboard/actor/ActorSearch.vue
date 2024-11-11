<script setup>

import EditCommon from "~/components/dashboard/common/EditCommon.vue";
import ActorEdit from "~/components/dashboard/actor/actor/ActorEdit.vue";
import {saveElement} from "~/composables/save_elements.js";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
})
const emits = defineEmits(['close-dialog'])
const dialog = ref(false)
function saveActor() {
  console.log('saveActor')
}

function saveItem({res, is_new}) {
  console.log('saveItem', res, is_new)
  // saveElement(props.collection_data, props.main).then((res) => {
  //   props.results.unshift(res)
  // })
}

</script>

<template>
  <v-card>
    <v-card-title class="text-h5 d-flex">
      <span v-if="!full_main.id">
        Nuevo actor
      </span>
      <span v-else>
        Editar actor
      </span>
      <v-spacer></v-spacer>
      <v-btn
        icon="close"
        variant="text"
        @click="emits('close-dialog')"
      >
      </v-btn>
    </v-card-title>
    <EditCommon
      :full_main="full_main"
      collection_name="actor"
      @item-saved="saveItem"
    >
      <template #edit="{full_main}">
        <ActorEdit :full_main="full_main" />
      </template>
    </EditCommon>
<!--    <v-card-actions>-->
<!--      <v-spacer></v-spacer>-->
<!--      <v-btn color="blue darken-1" variant="text" @click="dialog = false">Cancelar</v-btn>-->
<!--      <v-btn color="blue darken-1" variant="text" @click="saveActor">Guardar</v-btn>-->
<!--    </v-card-actions>-->
  </v-card>
</template>

<style scoped>

</style>