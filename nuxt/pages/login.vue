<script setup>

import { ref, computed } from 'vue'
// import SectionTitle from "@/components/dashboard/organization/SectionTitle.vue";
// import ResetPassword from "@/components/dashboard/profile/ResetPassword.vue";
import authMix from "~/components/login/auth_mix.js";
import SectionTitle from "~/components/login/SectionTitle.vue";
import LoginMail from "~/components/login/LoginMail.vue";
const { rules } = authMix;

const props = defineProps({
  is_reset: {
    type: Boolean,
    required: false,
    default: false,
  },
  is_init: {
    type: Boolean,
    required: false,
    default: false,
  }
})
const alert_error = ref(false)
const error_message = ref(undefined)
const login_mail = ref(undefined)
const want_recovery = ref(false)
const login_mail_comp = ref("LoginMail")

// const { sendReset, sendLogin } = mapActions({
//   sendReset: 'auth/SEND_PASSWORD_RESET',
//   sendLogin: 'auth/LOGIN_MAIL',
// })
const texts = computed(() => {
  let dict = {}
  if (want_recovery.value) {
    dict.component = 'LoginMail'
    dict.title = 'Restablecer contraseña'
    dict.alternative_title = 'Escribe tu correo'
  }
  else if (props.is_reset) {
    dict.component = 'ResetPassword'
    dict.title = 'Escribe tu nueva contraseña'
    dict.alternative_title = ''
  }
  // else if (props.is_init) {
  //   dict.component = 'ResetPassword'
  //   dict.title = 'Para concluir tu registro, escribe tu nueva contraseña'
  //   dict.alternative_title = ''
  // }
  else{
    dict.component = 'LoginMail'
    dict.title = 'Inicia Sesión'
    dict.alternative_title = ''
  }
  return dict
})
// watch(() => want_recovery.value, (val) => {
//   console.log("want_recovery-watch", val)
// })
function setAlert(message){
  alert_error.value = !!message
  error_message.value = message
    ? typeof(message) == 'object'
      ? message.detail || message
      : JSON.stringify(message)
    : '---'
}
function wantRecovery(val=true){
  setAlert(false)
  want_recovery.value = val
}


</script>

<template>
  <v-row class="d-flex justify-center align-center text-center">
    <v-card
      width="620"
      class="mt-6 rounded-shaped mb-3"
      color="#bfe0de"
    >
      <div class="no-wrap my-3 pt-3">
        <SectionTitle
          :title="texts.title"
        />
        <div class="text-h6 text-grey-darken-1 my-2">
          {{texts.alternative_title}}
        </div>
      </div>
      <v-alert
        type="error"
        :model-value="alert_error"
        border="bottom"
        transition="scale-transition"
        class="mx-3"
      >{{error_message}}</v-alert>
<!--      <ResetPassword-->
<!--        v-if="texts.component === 'ResetPassword'"-->
<!--        @set-alert="setAlert($event)"-->
<!--        :want_recovery="want_recovery"-->
<!--        :is_init="is_init"-->
<!--      ></ResetPassword>-->
      <LoginMail
        ref="login_mail"
        @set-alert="setAlert($event)"
        :want_recovery="want_recovery"
        @want-recovery="wantRecovery($event)"
      />
    </v-card>
  </v-row>
</template>

<style scoped>
.no-wrap{
  word-break: normal !important;
}
</style>
