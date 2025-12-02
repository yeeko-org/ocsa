<script setup>
import {computed, onMounted, ref, watch} from 'vue'

const menu_drawer = ref(false)
import {useMainStore} from "~/store/index.js";
import {useAuthStore} from "~/store/auth.js";
import {storeToRefs} from "pinia";
const router = useRouter()
const config = useRuntimeConfig();

const mainStore = useMainStore()
const authStore = useAuthStore()
const { schemas, current_collection_data } = storeToRefs(mainStore)
const { is_full_editor } = storeToRefs(authStore);
// const { fetchCatalogs } = mainStore
const { logout } = authStore
const admin_url = config.public.adminUrl
console.log('ADMIN URL:', config.public.adminUrl, admin_url)
// const route = useRoute()

// onBeforeMount(() => {
//   console.log("cats_ready")
// //   fetchCatalogs().then(() => {
// //     console.log("cats_ready")
// //   })
// })

const disable_open = ref(false)
const group = ref(null)

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

function openIcon(val){
  // console.log('openIcon', val)
  disable_open.value = true
}

function openItem(ev, val){
  // console.log('openItem', val)
  // console.log('ev', ev)
  // console.log('disable_open', disable_open.value)
  if (!disable_open.value)
    router.push(`/dashboard/${val}`)
  disable_open.value = false
  // :to="`/dashboard/${collection.snake_name}`"
  // router.push(val)
}

watch(
  group, (val) => {
    // console.log('group', val)
    menu_drawer.value = false
  }
)

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
              v-if="collection.catalog_groups.length"
              :value="collection.snake_name"
              soubgroup
            >
              <template v-slot:activator="{ props, isOpen }">
                <v-list-item
                  v-bind="props"
                  exact
                  :title="collection.plural_name"
                  :prepend-icon="collection.icon || 'category'"
                  :base-color="collection.color || 'grey-darken-1'"
                  @click="openItem($event, collection.snake_name)"
                  :class="collection.level === 'primary' ? '' : '_ml-3'"
                  :active-class="collection.level === 'primary'
                    ? '' : 'font-weight-bold'"
                >
                  <template v-slot:append="{ isActive, select }">
                    <v-icon
                      @click="openIcon"
                    >
                      {{ isActive ? 'expand_less' : 'expand_more' }}
                    </v-icon>
                  </template>
                </v-list-item>
              </template>
              <v-list-item
                v-for="(sub_coll, i) in collection.catalog_groups"
                :key="i"
                exact
                :title="sub_coll.plural_name"
                :value="sub_coll.snake_name"
                _to="`/dashboard/catalog/${sub_item.key}`"
                :to="`/dashboard/catalog/${sub_coll.key_name}`"
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
              :disabled="!is_full_editor"
              :title="collection.plural_name"
            ></v-list-item>
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
    </v-main>
  </v-app>
</template>
