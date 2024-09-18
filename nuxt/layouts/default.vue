<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

const menu_drawer = ref(false)
const menu_content = [
  {
    title: 'Notas',
    component: "ProviderList",
    to: 'note',
    icon: 'newspaper',
    catalogs: [
      {title: 'Medios (Fuentes)', to: 'source'},
    ]
  },
  {
    title: 'Proyectos',
    component:"ControlFilter",
    to: 'project',
    // icon: 'corporate_fare'},
    // icon: 'flood'},
    // icon: 'stadium'},
    // icon: 'real_estate_agent'},
    // icon: 'holiday_village'},
    // icon: 'engineering'},
    icon: 'factory',
    catalogs: [
      {title: 'Tipos de extractivismo', to: 'extractivism_type'},
      {title: 'Estados de proyectos', to: 'status_project'},
      {title: 'Escalas', to: 'project_type'},
      {title: 'Afectaciones sociales', to: 'social_impact'},
      {title: 'Afectaciones ambientales', to: 'environment_impact'},
    ]

  },
  {
    title: 'Conflictos',
    component: "ControlFilter",
    to: 'conflict',
    icon: 'local_fire_department'
  },
  {
    title: 'Actores',
    component: "UpdateHome",
    to: 'actor',
    // icon: 'account_balance'
    icon: 'recent_actors',
    catalogs: [
      {title: 'Sectores', to: 'sector'},
      {title: 'Grupos de pertenencia', to: 'group'},
      {title: 'Tipo de participación', to: 'participation_type'},
      {title: 'Grupo de interés', to: 'interest_group'},
    ]
  },
  {
    title: 'Eventos',
    component: "ActivityHolder",
    to: 'event',
    // icon: 'work_history'
    icon: 'notifications_active',
    catalogs: [
      {title: 'Tipos de eventos', to: 'event_type'},
      {title: 'Roles en los eventos', to: 'event_role'},
    ]
  },
]

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
        <v-icon class="mr-3" v-if="false">
          current_component.icon
        </v-icon>
        <span>
          current_component.title
        </span>
        <v-btn
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
      <v-list nav>
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
            :key="item.title"
            :value="item.title"
          >
            <template v-slot:activator="{ props }">
              <v-list-item
                v-bind="props"
                :title="item.title"
                :value="item.title"
                :prepend-icon="item.icon"
                :to="`/dashboard/${item.to}`"
              ></v-list-item>
            </template>
            <v-list-item
              v-for="(sub_item, i) in item.catalogs"
              :key="i"
              _prepend-icon="category"
              :title="sub_item.title"
              :value="sub_item.title"
              :to="`/dashboard/catalog/${sub_item.to}`"
            ></v-list-item>
          </v-list-group>
          <v-list-item
            v-else
            :key="item.title"
            active-class="accent--text"
            :to="`/dashboard/${item.to}`"
            :prepend-icon="item.icon"
            :title="item.title"
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
