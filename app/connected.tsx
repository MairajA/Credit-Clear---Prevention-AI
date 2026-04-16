import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import AuthLayout from '@/components/auth/AuthLayout';

export default function ConnectedScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <View style={styles.iconWrap}>
          <View style={styles.blobLeft} />
          <View style={styles.blobRight} />
          <Ionicons name="checkmark-circle-outline" size={120} color="#662F89" />
        </View>

        <Text style={styles.title}>Chase connected successfully</Text>
        <Text style={styles.body}>We found 2 accounts. Select which to monitor.</Text>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/connected-banks')}>
            <Text style={styles.buttonText}>Sign In</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  iconWrap: { marginTop: 66, alignItems: 'center', justifyContent: 'center', height: 220 },
  blobLeft: { position: 'absolute', width: 130, height: 100, borderRadius: 40, backgroundColor: 'rgba(221, 177, 234, 0.35)', left: 60, top: 82 },
  blobRight: { position: 'absolute', width: 130, height: 100, borderRadius: 40, backgroundColor: 'rgba(221, 177, 234, 0.35)', right: 60, top: 92 },
  title: { textAlign: 'center', fontSize: 30, fontWeight: '800', color: '#1F1F3D', marginTop: 10, lineHeight: 38 },
  body: { textAlign: 'center', color: '#293149', fontSize: 16, marginTop: 12 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
});
