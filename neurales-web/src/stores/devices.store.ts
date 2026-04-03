import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { http as api } from '@/api/http'

export interface Device {
  device_id: number
  marque_modele: string
  serial_number?: string
  connection_type: string
  etat: string
  organisation_id: number
}

export const useDeviceStore = defineStore('device', () => {
  const items = ref<Device[]>([])
  const current = ref<Device | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isEmpty = computed(() => items.value.length === 0)

  const fetchDevices = async (limit: number = 50, offset: number = 0) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/devices', {
        params: { limit, offset }
      })
      items.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement des dispositifs'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchDeviceById = async (deviceId: number) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/devices/${deviceId}`)
      current.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement du dispositif'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createDevice = async (payload: Omit<Device, 'device_id' | 'organisation_id'>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/devices', payload)
      const device = response.data
      items.value.push(device)
      return device
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors de la création du dispositif'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateDevice = async (deviceId: number, payload: Partial<Omit<Device, 'device_id' | 'organisation_id'>>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.put(`/devices/${deviceId}`, payload)
      const device = response.data
      const index = items.value.findIndex(d => d.device_id === deviceId)
      if (index !== -1) {
        items.value[index] = device
      }
      if (current.value?.device_id === deviceId) {
        current.value = device
      }
      return device
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors de la mise à jour du dispositif'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteDevice = async (deviceId: number) => {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/devices/${deviceId}`)
      items.value = items.value.filter(d => d.device_id !== deviceId)
      if (current.value?.device_id === deviceId) {
        current.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors de la suppression du dispositif'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    items,
    current,
    isLoading,
    error,
    isEmpty,
    fetchDevices,
    fetchDeviceById,
    createDevice,
    updateDevice,
    deleteDevice,
  }
})
