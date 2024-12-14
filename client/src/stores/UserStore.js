import { defineStore } from "pinia";
import { onBeforeMount, ref } from "vue";
import axios from "axios";
import Cookies from "js-cookie";

const useUserStore = defineStore('UserStore', () => {
  const isAuth = ref(false);
  const username = ref('');
  const userId = ref();
  const superuser = ref(false);
  const otpRequired = ref(false);
  const otpVerified = ref(false);

  // Функция для логина
  async function login(username, password) {
    try {
      const r = await axios.post('/api/user/login/', {
        username: username,
        password: password
      });
      otpRequired.value = r.data.otp_required || false; // Обновляем статус, нужен ли OTP
      return r.data; // Возвращаем данные ответа для дальнейшей обработки
    } catch (e) {
      console.error("Login error:", e.response?.data || e.message);
      throw new Error(e.response?.data?.error || "Login failed");
    }
  }

  // Получаем информацию о текущем пользователе
  async function fetchUser() {
    try {
      const r = await axios.get('/api/user/info');
      isAuth.value = r.data.is_authenticated;
      username.value = r.data.user;
      userId.value = r.data.user_id;
      superuser.value = r.data.is_superuser;
      this.otpRequired = r.data.otpRequired;  // Данные otpRequired
      this.otpVerified = r.data.otpVerified;  // Данные otpVerified
      // Проверяем статус OTP
      const otpStatus = await axios.get('/api/user/otp-status');
      otpVerified.value = otpStatus.data.otp_good || false;
      otpRequired.value = otpStatus.data.otp_required || false; // Используем статус для определения необходимости OTP
    } catch (e) {
      console.error("Error fetching user info:", e.response?.data || e.message);
    }
  }

  // Функция для верификации OTP
  async function verifyOtp(otpCode) {
    try {
      axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

      const r = await axios.post('/api/user/otp-login/', { otp_code: otpCode });
      otpVerified.value = r.data.success || false;

      if (otpVerified.value) {
        await fetchUser(); // Обновляем информацию о пользователе после успешной верификации
      }
    } catch (e) {
      console.error("OTP verification error:", e.response?.data || e.message);
      throw new Error(e.response?.data?.error || "OTP verification failed");
    }
  }

  onBeforeMount(() => {
    fetchUser();
  });

  return {
    isAuth,
    username,
    userId,
    superuser,
    otpRequired,
    otpVerified,
    fetchUser,
    login,
    verifyOtp
  };
});

export default useUserStore;
