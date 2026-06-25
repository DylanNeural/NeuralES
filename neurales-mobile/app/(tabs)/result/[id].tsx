import { useEffect, useState } from "react";
import { View, Text, ScrollView, ActivityIndicator } from "react-native";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { getMyResult, type SessionResult } from "../../../src/api/results";

const MODE_LABELS: Record<string, string> = {
  eeg: "EEG",
  ecg: "ECG",
  emg: "EMG",
  eog: "EOG",
  alpha: "Alpha",
};

function formatDatetime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function durationMinutes(start: string | null, end: string | null): string {
  if (!start || !end) return "—";
  const diff = (new Date(end).getTime() - new Date(start).getTime()) / 60000;
  return `${Math.round(diff)} min`;
}

export default function ResultDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const navigation = useNavigation();
  const [session, setSession] = useState<SessionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!id) return;
    getMyResult(Number(id))
      .then((data) => {
        setSession(data);
        navigation.setOptions({ title: `Session #${data.session_id}` });
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <View className="flex-1 bg-surface items-center justify-center">
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  if (error || !session) {
    return (
      <View className="flex-1 bg-surface items-center justify-center px-6">
        <Text className="text-muted text-base text-center">
          Impossible de charger cette session.
        </Text>
      </View>
    );
  }

  const label = MODE_LABELS[session.mode] ?? session.mode.toUpperCase();

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerStyle={{ padding: 16 }}>
      <View className="bg-card border border-border rounded-xl p-5 mb-4">
        <Text className="text-muted text-xs uppercase tracking-widest mb-1">
          Type de session
        </Text>
        <Text className="text-white text-xl font-bold">{label}</Text>
      </View>

      <View className="bg-card border border-border rounded-xl p-5 mb-4">
        <Row label="Début" value={formatDatetime(session.started_at)} />
        <Row label="Fin" value={formatDatetime(session.ended_at)} />
        <Row label="Durée" value={durationMinutes(session.started_at, session.ended_at)} />
      </View>

      {session.notes ? (
        <View className="bg-card border border-border rounded-xl p-5">
          <Text className="text-muted text-xs uppercase tracking-widest mb-2">
            Notes du praticien
          </Text>
          <Text className="text-white text-sm leading-6">{session.notes}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View className="flex-row justify-between items-center py-2 border-b border-border last:border-b-0">
      <Text className="text-muted text-sm">{label}</Text>
      <Text className="text-white text-sm font-medium">{value}</Text>
    </View>
  );
}
