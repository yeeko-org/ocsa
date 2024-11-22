<script setup>

import { ref } from 'vue'

import authMix from "~/components/login/auth_mix.js";
const { rules } = authMix;

import {useAuthStore} from '~/store/auth.js'
const authStore = useAuthStore()
const { loginMail } = authStore

const props = defineProps({
  setPassword: {
    type: Function,
    required: false,
    default: () => {},
  },
  is_reset: {
    type: Boolean,
    required: false,
    default: false,
  },
  is_init: {
    type: Boolean,
    required: false,
    default: false,
  },
  want_recovery: {
    type: Boolean,
    required: false,
    default: false,
  },
})

const error_login = ref(false)
const loading_login = ref(false)
const login_form = ref(false)
const login_ref = ref(null)
const emit = defineEmits(['set-alert', 'want-recovery'])
const login_data = ref({})
const show_password = ref(false)
// const { want_recovery } = props

function wantRecovery(val=true){
  emit('set-alert', false)
  emit('want-recovery')
}

async function sendRecover(){
  // emit('send-recover')
  const data = {"email": login_data.value.email}
  store.dispatch("auth/SEND_PASSWORD_RESET", data)
    .then(res => {
      console.log("res", res)
      loading_login.value = false
      if (res.error){
        // this.$emit('set-alert', JSON.stringify(res.error.response.data))
        emit('set-alert', res.error.response.data)
        error_login.value = true
        login_data.value.password = "";
      }
      else{
        emit('set-alert', false)
        error_login.value = false
      }
    })
}

async function sendLogin(){
  const { valid } = await login_ref.value.validate()
  if (!valid)
    return
  loading_login.value = true
  console.log("login_data", login_data.value)
  const data = {
    username: login_data.value.email,
    password : login_data.value.password
  }
  loginMail(data).then(res => {
    console.log("res", res)
    loading_login.value = false
    if (res.error){
      // this.$emit('set-alert', JSON.stringify(res.error.response.data))
      emit('set-alert', res.error.response.data)
      error_login.value = true
      login_data.value.password = "";
    }
    else{
      emit('set-alert', false)
      error_login.value = false
    }
  })
  // store.dispatch("auth/LOGIN_MAIL", data)
  //   .then(res => {
  //     console.log("res", res)
  //     loading_login.value = false
  //     if (res.error){
  //       // this.$emit('set-alert', JSON.stringify(res.error.response.data))
  //       emit('set-alert', res.error.response.data)
  //       error_login.value = true
  //       login_data.value.password = "";
  //     }
  //     else{
  //       emit('set-alert', false)
  //       error_login.value = false
  //     }
  //   })
}

</script>

<template>
  <v-form
    ref="login_ref"
    v-model="login_form"
    _validate-on="lazy"
    class="d-flex flex-column align-center"
  >

    <v-card-text style="width: 450px;">
      <v-text-field
        v-model="login_data.email"
        label="Correo electrónico"
        name="email"
        variant="solo"
        type="email"
        :rules="[rules.email, rules.user_name]"
        class="mb-2"
      >
        <template #prepend-inner>
          <v-icon color="#de6eea">
            mail
          </v-icon>
        </template>
      </v-text-field>
      <v-text-field
        v-if="!want_recovery"
        v-model="login_data.password"
        :type="show_password ? 'text' : 'password'"
        name="password"
        id="password"
        :rules="[rules.required, rules.min]"
        variant="solo"
        :append-inner-icon="show_password ? 'visibility' : 'visibility_off'"
        label="Tu contraseña"
        hint="Escribe una contraseña segura"
        @keyup.enter="sendLogin"
        @click:append-inner="show_password = !show_password"
      >
        <template #prepend-inner>
          <v-icon color="#de6eea">
            lock
          </v-icon>
        </template>
      </v-text-field>
    </v-card-text>
    <v-card-actions class="mb-4 mx-3" style="width: 450px;">
      <v-btn
        v-if="!want_recovery"
        color="accent"
        :variant="error_login ? 'outlined' : 'tonal'"
        @click="wantRecovery()"
      >
        Recuperar contraseña
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        v-if="!want_recovery"
        color="accent"
        variant="elevated"
        @click="sendLogin()"
      >
        Iniciar sesión
      </v-btn>
      <v-btn
        v-else
        color="accent"
        :loading="loading_login"
        @click="sendRecover()"
      >Enviar correo</v-btn>
    </v-card-actions>
  </v-form>
</template>

<style scoped lang="scss">

</style>
