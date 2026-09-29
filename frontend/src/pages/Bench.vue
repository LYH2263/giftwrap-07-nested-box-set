<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const selected = ref([])
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function toggle(id) {
  const i = selected.value.indexOf(id)
  if (i >= 0) selected.value.splice(i, 1)
  else selected.value.push(id)
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    const q = selected.value.map((id) => `box_ids=${id}`).join('&')
    out.value = save
      ? await postJSON('/api/estimate', { box_ids: selected.value, save: true })
      : await getJSON(`/api/estimate?${q}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">多选 clean 礼盒合并试算：各盒面积先各自落地再汇总成一条 run，写入后按快照留档。</p>
    <div class="row">
      <button :disabled="busy || !selected.length" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy || !selected.length" @click="go(true)">写入用纸档</button>
      <span class="meta">已选 {{ selected.length }} 盒</span>
    </div>
    <ul class="pick-list">
      <li v-for="b in boxes" :key="b.id">
        <label>
          <input type="checkbox" :checked="selected.includes(b.id)" @change="toggle(b.id)" />
          <span>{{ b.name }}</span>
          <span class="meta">{{ b.length }}×{{ b.width }}×{{ b.height }} m</span>
        </label>
      </li>
    </ul>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m² 合计</span></div>
      <p class="stat-line" v-if="out.ribbon">丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m</p>
      <table class="box-table">
        <thead>
          <tr><th>盒名</th><th>尺寸 (m)</th><th>盒表面积 (m²)</th><th>用纸 (m²)</th></tr>
        </thead>
        <tbody>
          <tr v-for="b in out.boxes" :key="b.box_id">
            <td>{{ b.name }}</td>
            <td class="meta">{{ b.length }}×{{ b.width }}×{{ b.height }}</td>
            <td class="meta">{{ b.box_surface }}</td>
            <td>{{ b.paper_m2 }}</td>
          </tr>
        </tbody>
      </table>
      <BoxUnfold
        v-if="out.boxes.length === 1"
        :l="out.boxes[0].length"
        :w="out.boxes[0].width"
        :h="out.boxes[0].height"
        :paper-m2="out.boxes[0].paper_m2"
      />
    </div>
  </div>
</template>
