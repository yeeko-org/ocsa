<script setup>

import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";
import EditCommon from "~/components/dashboard/common/EditCommon.vue";
const props = defineProps({
  collection_data: Object,
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})
</script>


<template>
<!--  <EditCommon-->
<!--    :full_main="full_main"-->
<!--    :collection_data="collection_data"-->
<!--    :is_massive_edit="is_massive_edit"-->
<!--  >-->
<!--    <template #edit="{ full_main }">-->
      <v-col cols="12" class="pa-0 d-flex">
        <SelectGroup
          :main_object="full_main"
          filter_group_name="project_types"
          category_group_value="project_type"
        />
      </v-col>
<!--    </template>-->
<!--  </EditCommon>-->
</template>

<style scoped>

</style>