<script setup>

const props = defineProps({
  size: {
    type: String,
    default: "default",
  },
  collection_data: {
    type: Object,
    required: true,
  },
})

const dialog = ref(false)

function saveCollection() {
  console.log('saveCollection')
}


</script>

<template>
  <v-btn
    class="hidden-xs-only px-0"
    icon
    :size="size"
    @click="dialog = true"
  >
    <v-icon>question_mark</v-icon>
    <v-dialog
      v-model="dialog"
      max-width="1100"
    >
      <v-card>
        <v-card-title class="d-flex">
          <span class="">
            Acerca de {{collection_data.plural_name}}
          </span>
          <v-spacer></v-spacer>
          <v-btn
            icon
            variant="text"
            @click="dialog = false"
          >
            <v-icon>close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-textarea
            v-model="collection_data.help_text"
            label="Descripción"
            rows="4"
            auto-grow
          >

          </v-textarea>
          <v-code v-if="false">
            {{ collection_data }}
          </v-code>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="accent"
            variant="elevated"

          >
            Guardar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>


</template>

<style scoped>

</style>