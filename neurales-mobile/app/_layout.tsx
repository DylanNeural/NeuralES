import { useEffect } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { Slot, useRouter, useSegments } from "expo-router";
import { useAuthStore } from "../src/store/auth";
import "../global.css";

function AuthGuard() {
  const { token, isLoading } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    const inAuth = segments[0] === "(auth)";
    if (!token && !inAuth) {
      router.replace("/(auth)/login");
    } else if (token && inAuth) {
      router.replace("/(tabs)");
    }
  }, [token, isLoading, segments]);

  return <Slot />;
}

export default function RootLayout() {
  const loadToken = useAuthStore((s) => s.loadToken);

  useEffect(() => {
    loadToken();
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthGuard />
    </GestureHandlerRootView>
  );
}
