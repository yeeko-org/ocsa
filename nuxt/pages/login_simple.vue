<script setup>

import {computed, ref} from "vue";
import LoginMail from "~/components/login/LoginMail.vue";
import SectionTitle from "~/components/login/SectionTitle.vue";

const alert_error = ref(false)
const error_message = ref(undefined)

const texts = computed(() => {
  return {
    component: 'LoginMail',
    title: 'Inicia Sesión',
    alternative_title: '',
  }
})
function setAlert(message){
  alert_error.value = !!message
  error_message.value = message
    ? typeof(message) == 'object'
      ? message.detail || message
      : JSON.stringify(message)
    : '---'
}
</script>

<template>
  <v-row class="d-flex justify-center align-center text-center">
    <v-card
      width="620"
      class="mt-6 rounded-shaped mb-3"
      color="secondary"
    >
      <div class="no-wrap my-3 pt-3">
        <SectionTitle
          :title="texts.title"
        />
        <div class="text-h6 text-grey-darken-1 my-2">
          {{texts.alternative_title}}
        </div>
      </div>
<!--      <v-alert-->
<!--        type="error"-->
<!--        :model-value="alert_error"-->
<!--        border="bottom"-->
<!--        transition="scale-transition"-->
<!--        class="mx-3"-->
<!--      >{{error_message}}</v-alert>-->
      <LoginMail
        ref="login_mail"
        @set-alert="setAlert($event)"
        :want_recovery="false"
      />
    </v-card>
  </v-row>
</template>
