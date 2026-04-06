<script setup>
const menu_drawer = ref(false)
import {useMainStore} from "~/store/index.js";
import {useDashboardStore} from "~/store/dash.js";
import {useAuthStore} from "~/store/auth.js";
const config = useRuntimeConfig();

const mainStore = useMainStore()
const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const { schemas, current_collection_data, cats } = storeToRefs(mainStore)
const { global_snackbar, global_snackbar_message } = storeToRefs(dashboardStore)
const { is_full_editor } = storeToRefs(authStore);
// const { fetchCatalogs } = mainStore
const { logout } = authStore
const admin_url = config.public.adminUrl
// console.log('ADMIN URL:', config.public.adminUrl, admin_url)
// const route = useRoute()

// onBeforeMount(() => {
//   console.log("cats_ready")
// //   fetchCatalogs().then(() => {
// //     console.log("cats_ready")
// //   })
// })

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

const main_structure = [
  { snake_name: "note" },
  {
    snake_name: "article",
    children: [
      "scraped_record",
      "source_types",
      "discarded_reasons"
    ]
  },
  {
    snake_name: "project",
    children: [
      "project_types",
      "status_projects",
      "status_history"
    ]
  },
  { snake_name: "conflict" },
  // { snake_name: "status_history" },
  {
    snake_name: "impact",
    children: [ "impact_types" ]
  },
  {
    snake_name: "event",
    children: [
      "event_types",
      "purposes",
      "involved_roles"
    ]
  },
  {
    snake_name: "actor",
    children: [
      "belongs",
      "countries",
      "participants",
      "indigenous_groups",
      "sectors",
      "participant_types"
    ]
  },
  {
    snake_name: "location",
    children: ["states"]
  },
  {
    snake_name: "interest",
    children: [ "interest_types" ]
  },
  {
    snake_name: "displacement",
    children: [
      "dimensions",
      "population_sizes",
      "temporalities"
    ]
  },

]

const main_collections = computed(() => {
  if (!schemas.value.collections_dict) return []
  return main_structure.map(item => {
    const coll = schemas.value.collections_dict[item.snake_name] || {}
    const raw_children = item.children || []
    return {
      snake_name: item.snake_name,
      plural_name: coll.plural_name,
      icon: coll.icon,
      color: coll.color,
      level: coll.level,
      children: raw_children.length ? [
        {
          snake_name: item.snake_name,
          plural_name: coll.plural_name,
          to: `/dashboard/${item.snake_name}`,
          color: coll.color,
          is_primary: true,
          title: `Ver ${coll.plural_name}`,
          key: `sub-${item.snake_name}`,
        },
        ...raw_children.map(child_key => {
          let fg = cats.value.filter_groups.find(c => c.key_name === child_key)
          let to = `/dashboard/catalog/${child_key}`
          if (!fg) {
            fg = schemas.value.collections_dict[child_key]
            to = `/dashboard/${child_key}`
            console.warn(`No se encontró el filter group ${child_key}`)
          }
          return {
            snake_name: child_key,
            key: child_key,
            plural_name: fg.plural_name,
            to,
          }
        }),
      ] : [],
    }
  })
})


</script>

<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
      flat
      class="mt-n1"
      clipped-left
      height="48"
    >
      <v-app-bar-nav-icon
        @click.stop="menu_drawer = !menu_drawer"
        color="white"
        class="mt-1"
      ></v-app-bar-nav-icon>
      <client-only>
        <v-toolbar-title class="d-flex align-center mt-1">
          <v-icon class="mr-3" color="white">
            {{ collection_data.icon || (collection_data.parent
                  ? collection_data.parent.icon
                  : 'dashboard') }}
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
      </client-only>
      <v-spacer></v-spacer>
      <v-btn
        @click="logout"
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
      temporary
      mobile-breakpoint="960"
      width="280"
    >
      <v-list nav open-strategy="multiple" _active-class="text-primary">
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
        <client-only>
          <template
            v-for="collection in main_collections"
            :key="collection.snake_name"
          >
            <v-list-group
              v-if="collection.children.length"
              :value="collection.snake_name"
              soubgroup
            >
              <template v-slot:activator="{ props }">
                <v-list-item
                  v-bind="props"
                  :title="collection.plural_name"
                  :prepend-icon="collection.icon || 'category'"
                  :base-color="collection.color || 'grey-darken-1'"
                  :class="collection.level === 'primary' ? '' : '_ml-3'"
                  :active-class="collection.level === 'primary'
                    ? '' : 'font-weight-bold'"
                ></v-list-item>
              </template>
              <v-list-item
                v-for="sub_coll in collection.children"
                :key="sub_coll.key"
                exact
                :title="sub_coll.title || sub_coll.plural_name"
                :value="sub_coll.snake_name"
                :to="sub_coll.to"
                :base-color="sub_coll.color"
              ></v-list-item>
            </v-list-group>
            <v-list-item
              v-else
              :value="collection.snake_name"
              exact
              _active-class="text-accent"
              :to="`/dashboard/${collection.snake_name}`"
              :prepend-icon="collection.icon"
              :base-color="collection.color || 'grey-darken-1'"
              :title="collection.plural_name"
            ></v-list-item>
<!--              :disabled="!is_full_editor"-->
            <v-divider></v-divider>
          </template>
        </client-only>
        <v-divider></v-divider>
        <v-list-item
          :to="`/dashboard/activity/`"
          title="Registro de Actividad"
        >
          <template v-slot:prepend>
            <v-icon color="accent">keyboard</v-icon>
          </template>

        </v-list-item>
        <v-divider></v-divider>
        <v-list-item
          :href="`${admin_url}/profile_auth/user/`"
          target="_blank"
          title="Gestión de usuarios"
        >
          <template v-slot:prepend>
            <v-icon color="accent">manage_accounts</v-icon>
          </template>

        </v-list-item>
        <v-list-item
          :href="`${admin_url}/work_flux/statuscontrol/`"
          target="_blank"
          title="Gestión de status"
        >
          <template v-slot:prepend>
            <v-icon color="accent">hub</v-icon>
          </template>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container
        _style="width: 100%;"
        class="pt-0"
        fluid
      >
        <v-layout align-center justify-center >
          <client-only>
            <NuxtPage/>
          </client-only>
        </v-layout>
      </v-container>
      <v-snackbar
        v-model="global_snackbar"
        color="success"
        location="right bottom"
        location-strategy="connected"
        timeout="4000"
      >
        {{ global_snackbar_message || 'Cambios guardados' }}
        <template v-slot:actions>
          <v-btn
            color="accent"
            variant="text"
            @click="global_snackbar = false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-main>
  </v-app>
</template>
