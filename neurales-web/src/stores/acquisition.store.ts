import { defineStore } from "pinia";
import { startAcquisition, stopAcquisition, type LiveMetrics } from "@/api/acquisition.api";

let ws: WebSocket | null = null;

type ElectrodeSelectionState = {
	selectedElectrodes: string[];
	lastClickedElectrode: string | null;
	sessionId: string | null;
	isRunning: boolean;
	streamStatus: "idle" | "connecting" | "open" | "closed" | "error";
	liveMetrics: LiveMetrics | null;
	qualityByElectrode: Record<string, number>;
};

function clamp(value: number, min: number, max: number) {
	return Math.min(max, Math.max(min, value));
}

function buildWsUrl() {
	const base = (import.meta.env.VITE_WS_BASE_URL || import.meta.env.VITE_API_BASE_URL || "http://localhost:8000") as string;
	const urlBase = base.startsWith("http") ? base.replace(/^http/, "ws") : base;
	const normalized = urlBase.replace(/\/$/, "");
	const wsUrl = `${normalized}/eeg/stream`;
	console.log("[AcquisitionStore] WebSocket URL:", wsUrl);
	return wsUrl;
}

function channelMatches(electrodeId: string, channel: string) {
	const upperElectrode = electrodeId.toUpperCase();
	const upperChannel = channel.toUpperCase();
	if (upperChannel === upperElectrode) return true;
	const parts = upperChannel.split(/[-_\s]/g);
	return parts.includes(upperElectrode);
}

function qualityFromSamples(samples: number[] | undefined, base: number) {
	if (!samples || samples.length === 0) return base;
	const meanAbs = samples.reduce((acc, v) => acc + Math.abs(v), 0) / samples.length;
	return clamp(base - meanAbs * 0.4, 0, 100);
}

export const useAcquisitionStore = defineStore("acquisition", {
	state: (): ElectrodeSelectionState => ({
		selectedElectrodes: [],
		lastClickedElectrode: null,
		sessionId: null,
		isRunning: false,
		streamStatus: "idle",
		liveMetrics: null,
		qualityByElectrode: {},
	}),
	actions: {
		toggleElectrode(electrodeId: string) {
			const idx = this.selectedElectrodes.indexOf(electrodeId);
			const isSelected = idx === -1;
			if (isSelected) this.selectedElectrodes.push(electrodeId);
			else this.selectedElectrodes.splice(idx, 1);
			this.lastClickedElectrode = electrodeId;
			this.syncQualityMap();
			return isSelected;
		},
		setSelectedElectrodes(electrodeIds: string[]) {
			this.selectedElectrodes = [...new Set(electrodeIds)];
			this.syncQualityMap();
		},
		clearSelectedElectrodes() {
			this.selectedElectrodes = [];
			this.lastClickedElectrode = null;
			this.syncQualityMap();
		},
		syncQualityMap() {
			const selectedSet = new Set(this.selectedElectrodes);
			Object.keys(this.qualityByElectrode).forEach((id) => {
				if (!selectedSet.has(id)) delete this.qualityByElectrode[id];
			});
			this.selectedElectrodes.forEach((id) => {
				if (this.qualityByElectrode[id] === undefined) {
					this.qualityByElectrode[id] = 0;
				}
			});
		},
		async startSession() {
			if (this.isRunning) return;
			try {
				const data = await startAcquisition();
				this.sessionId = data.session_id;
			} catch {
				this.sessionId = `local-${Date.now()}`;
			}
			this.isRunning = true;
			this.connectStream();
		},
		async stopSession() {
			if (!this.sessionId) return;
			const sessionId = this.sessionId;
			this.isRunning = false;
			this.sessionId = null;
			this.disconnectStream();
			try {
				await stopAcquisition(sessionId);
			} catch {
				// noop
			}
		},
		connectStream() {
			if (ws) return;
			this.streamStatus = "connecting";
			this.syncQualityMap();
			const wsUrl = buildWsUrl();
			console.log("[AcquisitionStore] Connecting to WebSocket...");
			ws = new WebSocket(wsUrl);
			ws.onopen = () => {
				console.log("[AcquisitionStore] WebSocket connected");
				this.streamStatus = "open";
			};
			ws.onclose = (evt) => {
				console.log("[AcquisitionStore] WebSocket closed", evt.code, evt.reason);
				this.streamStatus = this.isRunning ? "closed" : "idle";
				ws = null;
			};
			ws.onerror = (err) => {
				console.error("[AcquisitionStore] WebSocket error", err);
				this.streamStatus = "error";
			};
			ws.onmessage = (evt) => {
				try {
					const payload = JSON.parse(evt.data) as {
						t0: number;
						sfreq: number;
						channels: string[];
						samples: number[][];
						fatigue: number;
						quality: string;
						alerts: string[];
						chunk_seconds: number;
						window_seconds: number;
						error?: string;
					};
					if (payload.error) {
						console.error("[AcquisitionStore] Stream error:", payload.error);
						this.streamStatus = "error";
						return;
					}
					const qualityMap: Record<string, number> = { Good: 85, Fair: 60, Poor: 35 };
					const baseQuality = qualityMap[payload.quality] ?? 75;
					this.liveMetrics = {
						fatigue_score: payload.fatigue,
						quality: baseQuality,
						timestamp: new Date().toISOString(),
					};
					this.selectedElectrodes.forEach((id) => {
						const idx = payload.channels.findIndex((ch) => channelMatches(id, ch));
						const samples = idx >= 0 ? payload.samples[idx] : undefined;
						const jitter = (Math.random() - 0.5) * 10;
						this.qualityByElectrode[id] = clamp(
							qualityFromSamples(samples, baseQuality) + jitter,
							0,
							100
						);
					});
				} catch (err) {
					console.error("[AcquisitionStore] Failed to parse message", err);
					this.streamStatus = "error";
				}
			};
		},
		disconnectStream() {
			if (ws) {
				ws.close();
				ws = null;
			}
			this.streamStatus = "idle";
		},
	},
});