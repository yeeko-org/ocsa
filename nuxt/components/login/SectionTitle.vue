<script>
export default {
  name: "SectionTitle",
  props: {
    title: {
      type: String,
      required: true,
    },
  },
}
</script>

<template>
  <span class="text-h4 my-3 text-accent">
    {{title}}
  </span>
</template>

<style scoped>
  .title_base{
    _color: #f28d79;
    color: #1d2696;
    ccolor: black;
    font-weight: bolder;
    word-break: normal !important;
  }
</style>
