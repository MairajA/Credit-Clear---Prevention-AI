import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

export default function WaitingVerificationScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Waiting for Verification</Text>
        <Text style={styles.body}>Lorem Ipsum is simply dummy text of the printing and typesetting industry.</Text>

        <View style={styles.spacer} />

        <Text style={styles.footerText}>
          By continuing, you authorize read-only access to your Chase account data per Plaid's end-user privacy policy.
          Credit Clear cannot move or transfer your funds.
        </Text>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/connected')}>
            <Text style={styles.buttonText}>Sign In</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 24, fontWeight: '800', color: '#1F1F3D', marginTop: 14 },
  body: { textAlign: 'center', color: '#293149', marginTop: 10, fontSize: 13, lineHeight: 18, paddingHorizontal: 16 },
  spacer: { flex: 1 },
  footerText: { textAlign: 'center', color: '#8A8A99', fontSize: 11, lineHeight: 15, marginBottom: 16 },
  bottomZone: { justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
});
