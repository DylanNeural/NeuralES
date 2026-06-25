import { View, Text, TouchableOpacity, Alert, ScrollView } from "react-native";
import { useAuthStore } from "../../src/store/auth";

function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export default function ProfileScreen() {
  const { patient, logout } = useAuthStore();

  function handleLogout() {
    Alert.alert(
      "Déconnexion",
      "Voulez-vous vous déconnecter ?",
      [
        { text: "Annuler", style: "cancel" },
        { text: "Se déconnecter", style: "destructive", onPress: () => logout() },
      ]
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerStyle={{ padding: 16 }}>
      <View className="bg-card border border-border rounded-xl p-5 mb-4">
        <View className="w-16 h-16 bg-primary/20 rounded-full items-center justify-center mb-4 self-center">
          <Text className="text-primary text-2xl font-bold">
            {patient?.prenom?.[0]?.toUpperCase() ?? "?"}
            {patient?.nom?.[0]?.toUpperCase() ?? ""}
          </Text>
        </View>
        <Text className="text-white text-xl font-bold text-center">
          {patient?.prenom} {patient?.nom}
        </Text>
        <Text className="text-muted text-sm text-center mt-1">
          Né(e) le {formatDate(patient?.date_naissance)}
        </Text>
      </View>

      <View className="bg-card border border-border rounded-xl p-5 mb-6">
        <Text className="text-muted text-xs uppercase tracking-widest mb-3">
          Informations
        </Text>
        <InfoRow label="Nom" value={patient?.nom ?? "—"} />
        <InfoRow label="Prénom" value={patient?.prenom ?? "—"} />
        <InfoRow label="Date de naissance" value={formatDate(patient?.date_naissance)} />
        <InfoRow label="ID patient" value={String(patient?.patient_id ?? "—")} />
      </View>

      <TouchableOpacity
        className="bg-red-900/40 border border-red-800 rounded-xl py-4 items-center"
        onPress={handleLogout}
        activeOpacity={0.7}
      >
        <Text className="text-red-400 font-semibold text-base">
          Se déconnecter
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View className="flex-row justify-between items-center py-2 border-b border-border last:border-b-0">
      <Text className="text-muted text-sm">{label}</Text>
      <Text className="text-white text-sm font-medium">{value}</Text>
    </View>
  );
}
