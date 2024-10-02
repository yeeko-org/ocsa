<script setup>
import { computed, onMounted, ref } from 'vue'

const menu_drawer = ref(false)
import { menu_content } from "~/composables/menu.js";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

const mainStore = useMainStore()
const { all_groups } = storeToRefs(mainStore)
const route = useRoute()
const group = computed(() => {
  // console.log('route', route)
  const group_name = route.params.group
  const dashboard = {
    title: 'Dashboard',
    icon: 'dashboard',
    key: 'dashboard',
  }
  return all_groups.value.find(g => g.key === group_name) || dashboard
})
// const icon = computed(() => group.value.icon || group.parent ?

</script>

<template>
  <v-app>
    <v-app-bar
      app
      color="cyan"
      dark
      flat
      class="mt-n1"
      clipped-left
    >
      <v-app-bar-nav-icon
        @click.stop="menu_drawer = !menu_drawer"
        color="white"
      ></v-app-bar-nav-icon>
      <v-toolbar-title class="d-flex align-center">
        <v-icon class="mr-3" color="white">
          {{ group.icon || (group.parent ? group.parent.icon : 'dashboard') }}
        </v-icon>
        <span class="text-white">
          {{ group.name }}
        </span>
        <v-btn
          v-if="false"
          icon="category"
          v-tooltip:bottom="'Categorías de ___'"
        ></v-btn>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn
        _click="logout"
        color="white"
        light
        outlined
        icon="logout"
        v-tooltip:bottom="'Cerrar sesión'"
      >
      </v-btn>
    </v-app-bar>
    <v-navigation-drawer
      v-model="menu_drawer"
      app
      expand-on-hover
      mobile-breakpoint="960"
      width="280"
      mini-variant
    >
      <v-list nav open-strategy="multiple">
        <v-list-item>
          <template v-slot:prepend v-if="false">
            <v-icon>dashboard</v-icon>
          </template>
          <v-list-item-title class="text-h6">
            Dashboard OCSA
          </v-list-item-title>
          <v-list-item-subtitle>
            Interfaz de gestión
          </v-list-item-subtitle>
        </v-list-item>
        <template
          v-for="item in menu_content"
        >
          <v-list-group
            v-if="item.catalogs"
            :key="item.name"
            :value="item.name"
          >
            <template v-slot:activator="{ props }">
              <v-list-item
                v-bind="props"
                :title="item.name"
                :value="item.name"
                :prepend-icon="item.icon"
                :to="`/dashboard/${item.key}`"
              ></v-list-item>
            </template>
            <v-list-item
              v-for="(sub_item, i) in item.catalogs"
              :key="i"
              _prepend-icon="category"
              :title="sub_item.name"
              :value="sub_item.name"
              _to="`/dashboard/catalog/${sub_item.key}`"
              :to="`/dashboard/${sub_item.key}`"
            ></v-list-item>
          </v-list-group>
          <v-list-item
            v-else
            :key="item.name"
            active-class="accent--text"
            :to="`/dashboard/${item.key}`"
            :prepend-icon="item.icon"
            :title="item.name"
          ></v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container style="width: 100%;">
        <client-only>
          <NuxtPage />
        </client-only>
      </v-container>
    </v-main>
  </v-app>
</template>
