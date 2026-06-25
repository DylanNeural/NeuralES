import { useEffect, useState, useCallback } from "react";
import {
  FlatList,
  View,
  Text,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { getMyResults, type SessionResult } from "../../src/api/results";

const MODE_LABELS: Record<string, string> = {
  eeg: "EEG",
  ecg: "ECG",
  emg: "EMG",
  eog: "EOG",
  alpha: "Alpha",
};

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function SessionCard({ item }: { item: SessionResult }) {
  const router = useRouter();
  const label = MODE_LABELS[item.mode] ?? item.mode.toUpperCase();

  return (
    <TouchableOpacity
      className="bg-card border border-border rounded-xl p-4 mb-3 mx-4"
      activeOpacity={0.7}
      onPress={() => router.push(`/(tabs)/result/${item.session_id}`)}
    >
      <View className="flex-row items-center justify-between mb-1">
        <Text className="text-white font-semibold text-base">{label}</Text>
        <View className="bg-primary/20 px-3 py-1 rounded-full">
          <Text className="text-primary text-xs font-medium">Session #{item.session_id}</Text>
        </View>
      </View>
      <Text className="text-muted text-sm">{formatDate(item.started_at)}</Text>
      {item.notes ? (
        <Text className="text-muted text-sm mt-1" numberOfLines={1}>
          {item.notes}
        </Text>
      ) : null}
    </TouchableOpacity>
  );
}

export default function ResultsScreen() {
  const [results, setResults] = useState<SessionResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = useCallback(async () => {
    try {
      const data = await getMyResults();
      setResults(data);
      setError(null);
    } catch {
      setError("Impossible de charger les résultats.");
    }
  }, []);

  useEffect(() => {
    fetchResults().finally(() => setLoading(false));
  }, [fetchResults]);

  async function handleRefresh() {
    setRefreshing(true);
    await fetchResults();
    setRefreshing(false);
  }

  if (loading) {
    return (
      <View className="flex-1 bg-surface items-center justify-center">
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  return (
    <View className="flex-1 bg-surface">
      <FlatList
        data={results}
        keyExtractor={(item) => String(item.session_id)}
        renderItem={({ item }) => <SessionCard item={item} />}
        contentContainerStyle={{ paddingVertical: 16 }}
        ListEmptyComponent={
          <View className="items-center justify-center mt-20">
            <Text className="text-muted text-base">
              {error ?? "Aucune session trouvée."}
            </Text>
          </View>
        }
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor="#6366f1"
          />
        }
      />
    </View>
  );
}
