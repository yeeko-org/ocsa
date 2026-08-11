<script setup>
import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";

import DisplayGroup from "~/components/dashboard/common/select/DisplayGroup.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  },
  is_simple: Boolean,
})


</script>
<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
    :width="200"
  >
    <template #icon>

    </template>
    <template #title>
      <DisplayGroup
        filter_group_name="participant_types"
        main_collection_name="participant"
        :main_object="main"
      />
    </template>
    <template #details>
<!--      <DisplayGroup-->
<!--        :main_object="main.actor_full"-->
<!--        filter_group_name="sectors"-->
<!--        main_collection_name="actor"-->
<!--        forced_level="subtype"-->
<!--      />-->
      <ActorCard
        :full_main="main.actor_full"
        is_simple
        style="width: 240px;"
      />
<!--      <TitleCommon-->
<!--        :title_text="main.actor_full.name"-->
<!--      ></TitleCommon>-->
      <ProjectMiniList
        :mentions="[{project_full: main.project}]"
      />
      <NoteTitle
        :main="main.note"
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>