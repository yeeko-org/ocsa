import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);

  if (localStorage.getItem("app_user")) {
    user.value = localStorage.getItem("app_user");
  }

  const getUser = computed(() => user.value);

  const setUser = (name) => {
    user.value = name;
  };

  return {
    user,
    setUser,
    getUser,
  };
});