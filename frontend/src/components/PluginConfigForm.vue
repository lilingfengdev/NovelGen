<template>
  <div class="plugin-config-form">
    <n-form :model="formData" label-placement="top" size="small">
      <template v-for="(property, key) in schema.properties" :key="key">
        <!-- 跳过 enabled 字段，因为它已经用开关显示了 -->
        <n-form-item 
          v-if="key !== 'enabled'" 
          :label="property.title || key"
        >
          <template #label>
            <div class="form-label">
              <span>{{ property.title || key }}</span>
              <n-tooltip v-if="property.description" trigger="hover">
                <template #trigger>
                  <span class="help-icon">?</span>
                </template>
                {{ property.description }}
              </n-tooltip>
            </div>
          </template>
          
          <!-- Boolean 类型 -->
          <n-switch
            v-if="property.type === 'boolean'"
            :value="formData[key]"
            @update:value="(val) => updateField(key, val)"
          />
          
          <!-- Number 类型 -->
          <n-input-number
            v-else-if="property.type === 'number'"
            :value="formData[key]"
            @update:value="(val) => updateField(key, val)"
            :min="property.minimum"
            :max="property.maximum"
            :step="property.multipleOf || 1"
            style="width: 100%;"
          />
          
          <!-- Enum/Select 类型 -->
          <n-select
            v-else-if="property.enum"
            :value="formData[key]"
            @update:value="(val) => updateField(key, val)"
            :options="getEnumOptions(property)"
          />
          
          <!-- Textarea 类型 -->
          <n-input
            v-else-if="property.format === 'textarea'"
            :value="formData[key]"
            @update:value="(val) => updateField(key, val)"
            type="textarea"
            :rows="3"
          />
          
          <!-- String 类型（默认） -->
          <n-input
            v-else
            :value="formData[key]"
            @update:value="(val) => updateField(key, val)"
            :placeholder="property.default ? `默认: ${property.default}` : ''"
          />
        </n-form-item>
      </template>
    </n-form>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { NForm, NFormItem, NInput, NInputNumber, NSwitch, NSelect, NTooltip } from 'naive-ui'

const props = defineProps({
  schema: {
    type: Object,
    required: true
  },
  value: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update'])

const formData = ref({})

// 初始化表单数据
function initFormData() {
  const data = {}
  if (props.schema.properties) {
    for (const [key, property] of Object.entries(props.schema.properties)) {
      // 优先使用传入的值，其次使用默认值
      if (props.value[key] !== undefined) {
        data[key] = props.value[key]
      } else if (property.default !== undefined) {
        data[key] = property.default
      } else {
        // 根据类型设置初始值
        if (property.type === 'boolean') {
          data[key] = false
        } else if (property.type === 'number') {
          data[key] = 0
        } else if (property.enum) {
          data[key] = property.enum[0]
        } else {
          data[key] = ''
        }
      }
    }
  }
  formData.value = data
}

// 更新字段
function updateField(key, value) {
  formData.value[key] = value
  emit('update', { ...formData.value })
}

// 获取枚举选项
function getEnumOptions(property) {
  if (!property.enum) return []
  
  return property.enum.map((value, index) => ({
    label: property.enumNames?.[index] || value,
    value: value
  }))
}

// 监听value变化
watch(() => props.value, () => {
  initFormData()
}, { deep: true })

onMounted(() => {
  initFormData()
})
</script>

<style scoped>
.plugin-config-form {
  padding: 8px 4px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
}

.help-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  cursor: help;
  transition: all 0.2s;
}

.help-icon:hover {
  background: rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.plugin-config-form :deep(.n-form-item-label) {
  font-size: 13px;
  font-weight: 500;
}

.plugin-config-form :deep(.n-form-item) {
  margin-bottom: 18px;
}

.plugin-config-form :deep(.n-input),
.plugin-config-form :deep(.n-input-number),
.plugin-config-form :deep(.n-select) {
  font-size: 13px;
}
</style>

