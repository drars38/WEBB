<script setup>
import axios from 'axios';
import { ref, onBeforeMount } from 'vue';
import { Modal } from 'bootstrap';

let modalInstance = null;
const modalRef = ref(null);  // Используем реф для модального окна // Global variable for modal instance
const tags = ref([]);
const tagToAdd = ref('');
const tagToEdit = ref('');

// New variables for storing stats related to tags
const tagStats = ref({
  count: 0,
  avg: 0,
  max: 0,
  min: 0,
});

// Fetch the list of tags
async function fetchTags() {
  try {
    const response = await axios.get('/api/tags/');
    tags.value = response.data;
  } catch (error) {
    console.error('Error fetching tags:', error);
  }
}

// Add a new tag
async function onTagAdd() {
  if (!tagToAdd.value.trim()) return;

  try {
    const response = await axios.post('/api/tags/', { name: tagToAdd.value.trim() });
    tags.value.push(response.data); // Add the new tag to the list
    tagToAdd.value = ''; // Clear the input field
  } catch (error) {
    console.error('Error adding tag:', error);
  }
}

// Delete a tag
async function onRemoveTag(tag) {
  try {
    await axios.delete(`/api/tags/${tag.id}/`);
    tags.value = tags.value.filter(t => t.id !== tag.id); // Remove tag from local list
  } catch (error) {
    console.error('Error deleting tag:', error);
  }
}

// Edit a tag
async function onTagEditClick(tag) {
  tagToEdit.value = { ...tag }; // Copy the tag's data to the edit form
  modalInstance = new Modal(modalRef.value); // Initialize the modal instance
  modalInstance.show();
}

// Close modal
function closeModal() {
  if (modalInstance) {
    modalInstance.hide(); // Hide the modal
  }
}

// Update tag details
async function onUpdateTag() {
  if (tagToEdit.value) {
    await axios.put(`/api/tags/${tagToEdit.value.id}/`, {
      name: tagToEdit.value.name,
    });
    await fetchTags();  // Перезагружаем список тегов
    closeModal();  // Закрываем модальное окно
  }
}


onBeforeMount(async () => {
  await fetchTags();
  await fetchTagStats();
});

// Fetch tag statistics
async function fetchTagStats() {
  try {
    const response = await axios.get('/api/tags/stats/');
    tagStats.value = response.data;
  } catch (error) {
    console.error('Error fetching tag stats:', error);
  }
}
</script>

<template>
  <div class="p-2">
    <!-- Add Tag Form -->
    <form @submit.prevent="onTagAdd">
      <div class="row">
        <div class="col">
          <div class="form-floating mb-2">
            <input type="text" class="form-control" v-model="tagToAdd" required />
            <label for="floatingInput">Enter new tag</label>
          </div>
        </div>

        <div class="col-auto">
          <button class="btn btn-primary">Add Tag</button>
        </div>
      </div>
    </form>
  </div>

  <!-- Tag Statistics -->
  <h3>Tag Statistics</h3>
  <p><strong>Total tags:</strong> {{ tagStats.count }}</p>
  <p><strong>Average tag ID:</strong> {{ tagStats.avg }}</p>
  <p><strong>Maximum tag ID:</strong> {{ tagStats.max }}</p>
  <p><strong>Minimum tag ID:</strong> {{ tagStats.min }}</p>

  <!-- List of tags -->
  <div>
    <div v-for="tag in tags" class="tag-item" :key="tag.id">
      <b>{{ tag.name }}</b>
      <button class="btn btn-success" @click="onTagEditClick(tag)">
        <i class="bi bi-pen-fill"></i>
      </button>
      <button class="btn btn-danger" @click="onRemoveTag(tag)">
        <i class="bi bi-x"></i>
      </button>
    </div>
  </div>

  <!-- Модальное окно для редактирования тэга -->
<div ref="modalRef" class="modal fade" tabindex="-1" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Редактировать тег</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close" @click="closeModal">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-floating mb-2">
          <input
            type="text"
            class="form-control"
            v-model="tagToEdit.name"
            required
          />
          <label for="floatingInput">Название тега</label>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal" @click="closeModal">Закрыть</button>
        <button type="button" class="btn btn-primary" @click="onUpdateTag">Сохранить изменения</button>
      </div>
    </div>
  </div>
</div>

</template>

<style scoped>
.tag-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid salmon;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-content: center;
  align-items: center;
  gap: 16px;
}
</style>
