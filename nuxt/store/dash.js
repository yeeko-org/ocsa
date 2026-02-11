import { defineStore } from 'pinia'

// import axios from "axios";
// let request = axios.CancelToken.source();

export const useDashboardStore = defineStore('dash', {
  state: () => ({
    global_snackbar: false,
    global_snackbar_message: '',
  }),
  actions: {
    showSnackbar(message = 'Cambios guardados') {
      this.global_snackbar_message = message
      this.global_snackbar = true
    }
  },
});