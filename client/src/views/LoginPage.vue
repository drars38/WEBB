<script setup>
import {onBeforeMount, ref} from "vue";
import { useRouter } from "vue-router";
import useUserStore from "@/stores/UserStore.js";
import axios from "axios";
import Cookies from "js-cookie";

const user = ref('');
const password = ref('');
const otp = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const userStore = useUserStore();
const router = useRouter();

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});
// Функция для авторизации пользователя
async function login() {
  errorMessage.value = ''; // Сбрасываем сообщение об ошибке
  isLoading.value = true;  // Показываем индикатор загрузки

  try {
    const response = await userStore.login(user.value, password.value); // Вызов логина через UserStore

    if (response.otp_required) {
      // Если OTP требуется, показываем форму для ввода OTP
      errorMessage.value = "Требуется ввод OTP-кода.";
    } else {
      // Если OTP не требуется, перенаправляем на главную
      await router.push('/');
    }
  } catch (error) {
    errorMessage.value = error.message || 'Ошибка входа'; // Отображение сообщения об ошибке
  } finally {
    isLoading.value = false; // Скрываем индикатор загрузки
  }
}

// Функция для проверки OTP
async function verifyOtp() {
  errorMessage.value = ''; // Сбрасываем сообщение об ошибке
  isLoading.value = true;  // Показываем индикатор загрузки

  try {
    await userStore.verifyOtp(otp.value); // Вызов проверки OTP через UserStore
    await router.push('/'); // Перенаправление на главную страницу после успешного входа
  } catch (error) {
    errorMessage.value = error.message || 'Ошибка при проверке OTP'; // Отображение сообщения об ошибке
  } finally {
    isLoading.value = false; // Скрываем индикатор загрузки
  }
}
</script>

<template>
  <div class="login-container">
    <h2>Вход в систему</h2>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-indicator">Загрузка...</div>

    <!-- Форма входа -->
    <form v-if="!userStore.otpRequired" @submit.prevent="login">
      <div class="form-group">
        <label for="username">Имя пользователя</label>
        <input
          id="user"
          v-model="user"
          type="text"
          placeholder="Введите имя пользователя"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">Пароль</label>
        <input
          id="password"
          v-model="password"
          type="password"
          placeholder="Введите пароль"
          required
        />
      </div>
      <button type="submit" class="btn" :disabled="isLoading">Войти</button>
    </form>

    <!-- Форма OTP -->
    <form v-if="userStore.otpRequired" @submit.prevent="verifyOtp">
      <div class="form-group">
        <label for="otp">Введите OTP</label>
        <input
          id="otp"
          v-model="otp"
          type="text"
          placeholder="Введите одноразовый пароль"
          required
        />
      </div>
      <button type="submit" class="btn" :disabled="isLoading">Проверить OTP</button>
    </form>
  </div>
</template>



<style scoped>
/* Стили остаются без изменений */
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

.btn {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}

.btn:hover {
  background-color: #0056b3;
}

.btn:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-bottom: 15px;
  text-align: center;
}

.loading-indicator {
  text-align: center;
  font-size: 14px;
  color: #555;
  margin-bottom: 15px;
}
</style>
