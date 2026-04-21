import { http } from "./http";
import { desktopInvoke, isDesktopRuntime } from "@/utils/desktop-runtime";

export type DeviceCreatePayload = {
	marque_modele: string;
	serial_number?: string;
	connection_type: string;
	etat: string;
};

export type DeviceListItem = {
	device_id: number;
	organisation_id: number;
	marque_modele: string;
	serial_number?: string | null;
	connection_type: string;
	etat: string;
};

export type DeviceDetail = DeviceListItem;

export async function listDevices(params?: { limit?: number; offset?: number }) {
	// TODO: Desktop mode idea:
	if (isDesktopRuntime()) {
	  return desktopInvoke<DeviceListItem[]>("list_devices");
	}

	// TODO: Web mode idea:
	const { data } = await http.get<DeviceListItem[]>("/devices", { params });
	return data;
}

export async function getDeviceById(deviceId: number) {
	// TODO: Desktop mode idea:
	if (isDesktopRuntime()) {
	  return desktopInvoke<DeviceDetail | null>("get_device_by_id", { deviceId });
	}

	// TODO: Web mode idea:
	const { data } = await http.get<DeviceDetail>(`/devices/${deviceId}`);
	return data;
}

export async function createDevice(payload: DeviceCreatePayload) {
	// TODO: Desktop mode idea:
	if (isDesktopRuntime()) {
	  return desktopInvoke<DeviceDetail>("create_device", { payload });
	}

	// TODO: Web mode idea:
	const { data } = await http.post<DeviceDetail>("/devices", payload);
	return data;
}

export async function updateDevice(deviceId: number, payload: Partial<DeviceCreatePayload>) {
	// TODO: Desktop mode idea:
	if (isDesktopRuntime()) {
	  return desktopInvoke<DeviceDetail | null>("update_device", { deviceId, payload });
	}

	// TODO: Web mode idea:
	const { data } = await http.put<DeviceDetail>(`/devices/${deviceId}`, payload);
	return data;
}

export async function deleteDevice(deviceId: number) {
	// TODO: Desktop mode idea:
	if (isDesktopRuntime()) {
	  return desktopInvoke<boolean>("delete_device", { deviceId });
	}

	// TODO: Web mode idea:
	const { data } = await http.delete(`/devices/${deviceId}`);
	return data;
}
