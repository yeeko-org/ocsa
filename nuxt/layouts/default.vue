<script setup>

</script>

<template>
  <v-responsive>
    <v-app>
      <v-main>
        <v-container fluid class="pa-0">
          <v-layout align-center justify-center fill-height>

            <client-only>
              <NuxtPage/>
            </client-only>
          </v-layout>
        </v-container>
      </v-main>
    </v-app>
  </v-responsive>
</template>
