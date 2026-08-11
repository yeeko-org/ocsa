<script setup>
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  all_actors: {
    type: Array,
    default: () => [],
  }
})

const actor_data = computed(() => {
  return props.all_actors.find(actor =>{
    // (actor.uid || actor.pre_data?.uid) === props.item.actor_uid)
    const uid = actor.uid || actor.pre_data?.id || actor.pre_data?.actor_full?.uid
    return uid === props.item.actor_uid
  })
})

</script>

<template>
  <div v-if="item.path && !item.id">
    <v-card
      color="blue"
      variant="tonal"
    >
      <ActorCard

        v-if="actor_data"
        :full_main="actor_data"
        title="PRE-REGISTRO"
        is_simple
      />
      <span v-else>
        <b>PRE-REGISTRO</b> -
        {{actor_data?.name || 'Desconocido'}}
      </span>
      ({{item.role_text}})
    </v-card>
<!--    <span v-if="!actor_data" class="text-body-2 text-warning">-->
<!--      {{all_actors}}-->

<!--    </span>-->
  </div>
</template>

<style scoped>

</style>