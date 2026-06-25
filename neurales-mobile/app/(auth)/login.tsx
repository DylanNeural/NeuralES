import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { useAuthStore } from "../../src/store/auth";
import { patientLogin, getPatientMe } from "../../src/api/auth";

export default function LoginScreen() {
  const [nom, setNom] = useState("");
  const [prenom, setPrenom] = useState("");
  const [dateNaissance, setDateNaissance] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);

  function handleDateChange(text: string) {
    // Strip non-digits, then auto-insert dashes: DD-MM-YYYY
    const digits = text.replace(/\D/g, "").slice(0, 8);
    let formatted = digits;
    if (digits.length > 2) formatted = digits.slice(0, 2) + "-" + digits.slice(2);
    if (digits.length > 4) formatted = formatted.slice(0, 5) + "-" + digits.slice(4);
    setDateNaissance(formatted);
  }

  async function handleLogin() {
    if (!nom.trim() || !prenom.trim() || !dateNaissance.trim() || !password) {
      Alert.alert("Erreur", "Tous les champs sont requis.");
      return;
    }
    // Convert JJ-MM-AAAA → YYYY-MM-DD for the API
    const parts = dateNaissance.trim().split("-");
    if (parts.length !== 3 || parts[0]!.length !== 2 || parts[1]!.length !== 2 || parts[2]!.length !== 4) {
      Alert.alert("Erreur", "Date invalide. Format attendu : JJ-MM-AAAA");
      return;
    }
    const isoDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
    setLoading(true);
    try {
      const { access_token } = await patientLogin({
        nom: nom.trim(),
        prenom: prenom.trim(),
        date_naissance: isoDate,
        password,
      });
      const patient = await getPatientMe(access_token);
      await login(access_token, patient);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number; data?: { detail?: string } } })?.response?.status;
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      const isNetwork = (err as { code?: string })?.code === "ERR_NETWORK" || !(err as { response?: unknown })?.response;
      console.error("[login] error", status, detail, err);
      if (isNetwork) {
        Alert.alert("Erreur réseau", `Impossible de joindre le serveur.\n${process.env.EXPO_PUBLIC_API_URL}`);
      } else {
        Alert.alert("Connexion échouée", detail ?? `Erreur ${status ?? "inconnue"}`);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      className="flex-1 bg-surface"
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView
        contentContainerStyle={{ flexGrow: 1, justifyContent: "center" }}
        className="px-6"
        keyboardShouldPersistTaps="handled"
      >
        <Text className="text-white text-3xl font-bold mb-2 text-center">
          NeuralES
        </Text>
        <Text className="text-muted text-base mb-10 text-center">
          Espace patient
        </Text>

        <TextInput
          className="bg-card border border-border text-white rounded-xl px-4 py-3 mb-4"
          placeholder="Nom"
          placeholderTextColor="#64748b"
          value={nom}
          onChangeText={setNom}
          autoCapitalize="words"
          autoCorrect={false}
        />
        <TextInput
          className="bg-card border border-border text-white rounded-xl px-4 py-3 mb-4"
          placeholder="Prénom"
          placeholderTextColor="#64748b"
          value={prenom}
          onChangeText={setPrenom}
          autoCapitalize="words"
          autoCorrect={false}
        />
        <TextInput
          className="bg-card border border-border text-white rounded-xl px-4 py-3 mb-4"
          placeholder="JJ-MM-AAAA"
          placeholderTextColor="#64748b"
          value={dateNaissance}
          onChangeText={handleDateChange}
          keyboardType="number-pad"
          maxLength={10}
          autoCorrect={false}
        />
        <TextInput
          className="bg-card border border-border text-white rounded-xl px-4 py-3 mb-8"
          placeholder="Mot de passe"
          placeholderTextColor="#64748b"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity
          className="bg-primary rounded-xl py-4 items-center"
          onPress={handleLogin}
          disabled={loading}
          activeOpacity={0.8}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text className="text-white font-semibold text-base">
              Se connecter
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
