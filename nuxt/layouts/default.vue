<script setup>
import { computed, onMounted, ref } from 'vue'

const menu_drawer = ref(false)
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

const mainStore = useMainStore()
const { schemas, current_collection_data } = storeToRefs(mainStore)
// const { fetchCatalogs } = mainStore
const route = useRoute()

onBeforeMount(() => {
  console.log("cats_ready")
//   fetchCatalogs().then(() => {
//     console.log("cats_ready")
//   })
})


const collection_data = computed(() => {
  // console.log('route', route)
  // const group_name = route.params.group
  const dashboard = {
    title: 'Dashboard',
    name: 'Dashboard',
    plural_name: 'Dashboard',
    icon: 'dashboard',
    key: 'dashboard',
  }
  // return all_groups.value.find(g => g.key === group_name) || dashboard
  return current_collection_data.value || dashboard
})
  // let main_collections = data.collections.filter(
  //   coll => ['primary', 'secondary'].includes(coll.level))
const main_collections = computed(() => {
  if (!schemas.value.collections) return []
  return schemas.value.collections.filter(
    coll => ['primary', 'secondary'].includes(coll.level))
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
          {{ collection_data.icon || (collection_data.parent ? collection_data.parent.icon : 'dashboard') }}
        </v-icon>
        <span class="text-white">
          {{ collection_data.plural_name }}
        </span>
        <v-btn
          v-if="false"
          icon="category"
          _v-tooltip:bottom="'Categorías de ___'"
        ></v-btn>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn
        _click="logout"
        color="white"
        light
        outlined
        icon="logout"
        _v-tooltip:bottom="'Cerrar sesión'"
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
        <v-divider></v-divider>
        <template
          v-for="collection in main_collections"
        >
          <v-list-group
            v-if="collection.catalog_groups.length"
            :key="collection.snake_name"
            :value="collection.name"
          >
            <template v-slot:activator="{ props }">
              <v-list-item
                v-bind="props"
                :title="collection.plural_name"
                :value="collection.snake_name"
                :prepend-icon="collection.icon || 'category'"
                :base-color="collection.color ? `${collection.color}` : 'grey-darken-1'"
                :to="`/dashboard/${collection.snake_name}`"
                _to="`/dashboard/catalog/${sub_item.key}`"
                :class="collection.level === 'primary' ? '' : 'ml-2'"
              ></v-list-item>
            </template>
            <v-list-item
              v-for="(sub_coll, i) in collection.catalog_groups"
              :key="i"
              _prepend-icon="category"
              :title="sub_coll.name"
              :value="sub_coll.key_name"
              _to="`/dashboard/catalog/${sub_item.key}`"
              :to="`/dashboard/catalog/${sub_coll.key_name}`"
            ></v-list-item>
          </v-list-group>
          <v-list-item
            v-else
            :key="collection.snake_name"
            active-class="accent--text"
            :to="`/dashboard/${collection.snake_name}`"
            :prepend-icon="collection.icon"
            :title="collection.name"
          ></v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container
        style="width: 100%;"
        class="pt-0"
      >
        <client-only>
          <NuxtPage/>
        </client-only>
      </v-container>
    </v-main>
  </v-app>
</template>
