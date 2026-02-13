<template>
  <div class="user-info-form">
    <h2 class="form-title">Vamos começar.</h2>
    <p class="form-subtitle">Precisamos de alguns dados para criar o teu perfil.</p>

    <form @submit.prevent="submitForm" class="form-grid">
      <div class="form-group">
        <label for="gender">Género</label>
        <select id="gender" v-model="form.gender">
          <option value="male">Masculino</option>
          <option value="female">Feminino</option>
          <option value="other">Outro</option>
        </select>
      </div>

      <div class="form-group">
        <label for="age">Idade</label>
        <input type="number" id="age" v-model.number="form.age" placeholder="25" />
      </div>

      <div class="form-group">
        <label for="height">Altura (cm)</label>
        <input type="number" id="height" v-model.number="form.height" placeholder="175" />
      </div>

      <div class="form-group">
        <label for="weight">Peso (kg)</label>
        <input type="number" id="weight" v-model.number="form.weight" placeholder="70" />
      </div>

      <div class="form-group full-width">
        <label>Objetivo Principal</label>
        <div class="radio-group">
          <label class="radio-label">
            <input type="radio" name="goal" value="lose" v-model="form.goal" />
            Perder Peso
          </label>
          <label class="radio-label">
            <input type="radio" name="goal" value="maintain" v-model="form.goal" />
            Manter Peso
          </label>
          <label class="radio-label">
            <input type="radio" name="goal" value="gain" v-model="form.goal" />
            Ganhar Massa
          </label>
        </div>
      </div>

      <div class="form-group full-width">
        <label>Nível de Atividade</label>
        <div class="radio-group">
          <label class="radio-label">
            <input type="radio" name="activity" value="sedentary" v-model="form.activityLevel" />
            Sedentário
          </label>
          <label class="radio-label">
            <input type="radio" name="activity" value="light" v-model="form.activityLevel" />
            Leve
          </label>
          <label class="radio-label">
            <input type="radio" name="activity" value="moderate" v-model="form.activityLevel" />
            Moderado
          </label>
          <label class="radio-label">
            <input type="radio" name="activity" value="high" v-model="form.activityLevel" />
            Elevado
          </label>
        </div>
      </div>

      <div class="form-group full-width">
        <label for="allergies">Alergias ou Restrições (separadas por vírgula)</label>
        <input type="text" id="allergies" v-model="form.allergies" placeholder="Ex: glúten, lactose" />
      </div>

      <div class="form-actions full-width">
        <button type="submit" class="btn btn-primary">Criar Perfil</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';

const form = reactive({
  gender: 'male',
  age: null,
  height: null,
  weight: null,
  goal: 'maintain',
  activityLevel: 'sedentary',
  allergies: '',
});

const submitForm = () => {
  // Aqui ficará a lógica para enviar os dados para o backend
  console.log('Form data:', form);
  alert('Perfil criado com sucesso! (Ver dados na consola)');
};
</script>

<style scoped>
/* Cores e estilos adaptados do App.vue */
.user-info-form {
  --bg-main: #f4fbf8;
  --bg-soft: #ffffff;
  --text-main: #13293d;
  --text-muted: #3b566d;
  --accent: #0f766e;
  --accent-hover: #0b5c56;
  --line: #d7e7e0;

  max-width: 720px;
  margin: 40px auto;
  padding: 28px;
  background: var(--bg-soft);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.07);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  color: var(--text-main);
}

.form-title {
  margin: 0 0 8px;
  font-size: 2.1rem;
  letter-spacing: -0.02em;
  color: var(--text-main);
}

.form-subtitle {
  margin: 0 0 24px;
  font-size: 1.05rem;
  color: var(--text-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
}

.form-group input[type='text'],
.form-group input[type='number'],
.form-group select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fdfdfd;
  font-size: 1rem;
  font-family: inherit;
  color: var(--text-main);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 4px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
  background: var(--bg-soft);
  transition: border-color 0.2s, background-color 0.2s;
}

.radio-label:hover {
  border-color: #b8d5cb;
}

.radio-label input[type='radio'] {
  accent-color: var(--accent);
}

input[type='radio']:checked + .radio-label {
    border-color: var(--accent);
    background-color: #f0fafa;
}

.form-actions {
  margin-top: 24px;
  text-align: right;
}

.btn {
  border-radius: 999px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
}

.btn-primary {
  border: 0;
  background: var(--accent);
  color: #f2fffc;
  box-shadow: 0 4px 14px rgba(15, 118, 110, 0.2);
}

.btn-primary:hover {
  background: var(--accent-hover);
  box-shadow: 0 6px 18px rgba(15, 118, 110, 0.28);
}
</style>
