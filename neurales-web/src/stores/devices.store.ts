import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as DevicesAPI from '@/api/devices.api'

export interface Device {
  device_id: number
  marque_modele: string
  serial_number?: string | null
  connection_type: string
  etat: string
  organisation_id: number
}

type DevicePayload = DevicesAPI.DeviceCreatePayload

export const useDeviceStore = defineStore('device', () => {
  const items = ref<Device[]>([])
  const current = ref<Device | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isEmpty = computed(() => items.value.length === 0)

  const toErrorMessage = (err: unknown, fallback: string): string => {
    const e = err as any
    return e?.response?.data?.detail || e?.message || (typeof e === 'string' ? e : fallback)
  }

  const fetchDevices = async (limit: number = 50, offset: number = 0) => {
    isLoading.value = true
    error.value = null
    try {
      items.value = (await DevicesAPI.listDevices({ limit, offset })) || []
    } catch (err: any) {
      error.value = toErrorMessage(err, 'Erreur lors du chargement des dispositifs')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchDeviceById = async (deviceId: number) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await DevicesAPI.getDeviceById(deviceId)
      if (!response) throw new Error('Dispositif introuvable')
      current.value = response
      return response
    } catch (err: any) {
      error.value = toErrorMessage(err, 'Erreur lors du chargement du dispositif')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createDevice = async (payload: DevicePayload) => {
    isLoading.value = true
    error.value = null
    try {
      const device = await DevicesAPI.createDevice(payload)
      items.value.push(device)
      return device
    } catch (err: any) {
      error.value = toErrorMessage(err, 'Erreur lors de la création du dispositif')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateDevice = async (deviceId: number, payload: Partial<DevicePayload>) => {
    isLoading.value = true
    error.value = null
    try {
      const device = await DevicesAPI.updateDevice(deviceId, payload)
      if (!device) throw new Error('Dispositif introuvable')
      const index = items.value.findIndex(d => d.device_id === deviceId)
      if (index !== -1) {
        items.value[index] = device
      }
      if (current.value?.device_id === deviceId) {
        current.value = device
      }
      return device
    } catch (err: any) {
      error.value = toErrorMessage(err, 'Erreur lors de la mise à jour du dispositif')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteDevice = async (deviceId: number) => {
    isLoading.value = true
    error.value = null
    try {
      await DevicesAPI.deleteDevice(deviceId)
      items.value = items.value.filter(d => d.device_id !== deviceId)
      if (current.value?.device_id === deviceId) {
        current.value = null
      }
    } catch (err: any) {
      error.value = toErrorMessage(err, 'Erreur lors de la suppression du dispositif')
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
