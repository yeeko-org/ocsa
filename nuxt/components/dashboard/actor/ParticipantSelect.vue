<script setup>
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";
import { useRules } from '~/composables/useRules'

const props = defineProps({
  all_actors: { type: Array, default: () => [] }
})
const model = defineModel({ required: true })
const { rules } = useRules()

const registered_actors = computed(() => props.all_actors.filter(a => a.id))
</script>

<template>
  <v-select
    v-model="model"
    :items="registered_actors"
    item-title="name"
    item-value="id"
    label="Participante"
    variant="outlined"
    class="mr-2"
    :rules="[rules.required]"
  >
    <template #item="{ item, props: { onClick, value } }">
      <v-list-item @click="onClick" :value="value">
        <template v-slot:default>
          <ActorCard :full_main="item.raw" :title="item.title" is_simple />
        </template>
      </v-list-item>
    </template>
    <template #selection="{ item }">
      <ActorCard :full_main="item.raw" :title="item.name" is_simple />
    </template>
  </v-select>
</template>

<style scoped>

</style>
