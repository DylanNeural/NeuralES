import { isDesktopRuntime } from '@/utils/desktop-runtime';
import { invoke } from '@tauri-apps/api/core';
import { http as api } from '@/api/http';

class SyncWorker {
  private isSyncing = false;
  private timer: number | null = null;

  start(intervalMs = 30000) {
    // Le Worker ne tourne que sur l'application Desktop (Tauri)
    if (!isDesktopRuntime()) return;

    // Synchroniser dès que la connexion internet revient
    window.addEventListener('online', () => this.syncNow());

    // Synchroniser régulièrement en tâche de fond (toutes les 30s par défaut)
    this.timer = window.setInterval(() => {
      if (navigator.onLine) this.syncNow();
    }, intervalMs);

    // Lancer une première synchro au démarrage après un court délai
    if (navigator.onLine) {
      setTimeout(() => this.syncNow(), 3000);
    }
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    window.removeEventListener('online', () => this.syncNow());
  }

  async syncNow() {
    // Si déjà en cours ou pas d'internet, on annule
    if (this.isSyncing || !navigator.onLine) return;
    
    this.isSyncing = true;
    console.log("🔄 [SyncWorker] Début de la synchronisation...");

    try {
      // 1. Synchronisation des Patients
      await this.syncEntity('patients', 'get_pending_patients', 'resolve_patient_sync');
      
      // 2. Synchronisation des Dispositifs
      await this.syncEntity('devices', 'get_pending_devices', 'resolve_device_sync');
      
      // 3. Synchronisation des Sessions
      await this.syncEntity('results', 'get_pending_sessions', 'resolve_session_sync');

      console.log("✅ [SyncWorker] Synchronisation terminée avec succès.");
    } catch (error) {
      console.error("❌ [SyncWorker] Échec de la synchronisation:", error);
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Fonction générique pour traiter la file d'attente d'une entité (CRUD)
   */
  private async syncEntity(endpoint: string, fetchCommand: string, resolveCommand: string) {
    try {
      // Demande à Rust tous les éléments non-synchronisés (pending_insert, pending_update, pending_delete)
      const pendingItems = await invoke<any[]>(fetchCommand);
      
      if (!pendingItems || pendingItems.length === 0) return;
      console.log(`📦 [SyncWorker] ${pendingItems.length} éléments à synchroniser pour /${endpoint}`);

      for (const item of pendingItems) {
        try {
          const localId = item.patient_id || item.device_id || item.session_id;
          let remoteId = item.remote_id;
          
          if (item.sync_status === 'pending_insert') {
            const res = await api.post(`/${endpoint}`, item);
            // Récupère l'ID distant généré par l'API Web
            remoteId = res.data.id || res.data.patient_id || res.data.device_id || res.data.session_id || localId;
            await invoke(resolveCommand, { localId, remoteId, status: 'synced' });
          } 
          else if (item.sync_status === 'pending_update') {
            const targetId = remoteId || localId;
            await api.put(`/${endpoint}/${targetId}`, item);
            await invoke(resolveCommand, { localId, remoteId, status: 'synced' });
          } 
          else if (item.sync_status === 'pending_delete') {
            const targetId = remoteId || localId;
            await api.delete(`/${endpoint}/${targetId}`);
            // Supprime définitivement la ligne locale SQLite
            await invoke(resolveCommand, { localId, remoteId: null, status: 'deleted' });
          }
        } catch (err) {
          console.error(`❌ Erreur de synchro sur l'entité /${endpoint}:`, err);
        }
      }
    } catch (err) {
      console.warn(`⚠️ Commande Tauri '${fetchCommand}' non disponible.`, err);
    }
  }
}

export const syncWorker = new SyncWorker();