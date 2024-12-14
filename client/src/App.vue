<script setup>
import { onBeforeMount, watch } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { storeToRefs } from "pinia";
import useUserStore from "@/stores/UserStore.js";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const { isAuth, username, userId, superuser, otpRequired, otpVerified } = storeToRefs(userStore);
const router = useRouter();

// Получаем информацию о пользователе через API
onBeforeMount(async () => {
  try {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
    const response = await axios.get('/api/user/info/');

    // Обновляем данные в хранилище
    userStore.isAuth = response.data.is_authenticated;
    userStore.username = response.data.username;
    userStore.userId = response.data.user_id;
    userStore.superuser = response.data.is_superuser;
    userStore.otpRequired = response.data.otpRequired;
    userStore.otpVerified = response.data.otpVerified;
  } catch (error) {
    console.error('Ошибка при получении информации о пользователе:', error);
  }
});

async function logout() {
  try {
    await axios.post('/api/user/logout/');
    await userStore.fetchUser();
    await router.push('/');
  } catch (error) {
    console.error('Ошибка при выходе:', error);
  }
}
</script>

<template>
  <div class="sidebar-layout">
    <nav class="sidebar">
      <div class="menu-header">
        <i class="menu-icon">☰</i> <!-- Иконка меню -->
      </div>
      <ul class="menu-list">
        <li><router-link to="/">Главная</router-link></li>
        <li><router-link to="/authors">Авторы</router-link></li>
        <li><router-link to="/posts">Посты</router-link></li>
        <li><router-link to="/tags">Тэги</router-link></li>
        <li v-if="isAuth">
          <a href="#" @click="logout">Выйти</a>
        </li>
        <li v-else>
          <router-link to="/login">Войти</router-link>
        </li>
      </ul>
    </nav>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style lang="scss" scoped>
.sidebar-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 40px;
  background-color: #343a40;
  color: white;
  transition: width 0.3s ease;
  overflow: hidden;

  &:hover {
    width: 250px; /* Раскрывается при наведении */
  }

  .menu-header {
    display: flex;
    align-items: center;
    padding: 10px;
    gap: 10px;
    font-size: 18px;
    color: white;

    .menu-icon {
      font-size: 20px;
      cursor: pointer;
    }
  }

  .menu-list {
    display: none; /* По умолчанию список скрыт */
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      a {
        display: block;
        padding: 10px 15px;
        color: white;
        text-decoration: none;
        transition: background-color 0.2s;

        &:hover {
          background-color: #495057;
        }
      }
    }
  }

  &:hover .menu-list {
    display: block; /* Список появляется при наведении на меню */
  }
}

.content {
  flex-grow: 1;
  padding: 20px;
}
</style>
