import { Stack, useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useState } from 'react';

import AuthLayout from '@/components/auth/AuthLayout';

export default function SignInBankScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ bank?: string }>();
  const bankName = typeof params.bank === 'string' ? params.bank : 'your bank';
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Sign in to {bankName}</Text>
        <Text style={styles.body}>Your credentials go directly to {bankName} — we never see your password</Text>

        <View style={styles.securityBox}>
          <View style={styles.securityIcon}><Text style={{ color: '#662F89', fontWeight: '900' }}>⛨</Text></View>
          <View>
            <Text style={styles.securityTitle}>Secured by Plaid</Text>
            <Text style={styles.securitySub}>Bank-level 256-bit encryption</Text>
          </View>
        </View>

        <View style={styles.field}>
          <TextInput placeholder={`${bankName} username`} placeholderTextColor="#8A8A99" value={username} onChangeText={setUsername} style={styles.input} />
        </View>
        <View style={[styles.field, styles.passRow]}>
          <TextInput placeholder="Password" placeholderTextColor="#8A8A99" value={password} onChangeText={setPassword} secureTextEntry={!showPassword} style={[styles.input, { flex: 1 }]} />
          <Pressable onPress={() => setShowPassword((p) => !p)}>
            <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={18} color="#8A8A99" />
          </Pressable>
        </View>

        <Text style={styles.note}>{bankName} may send you a verification code to confirm your identity.</Text>

        <View style={styles.bottomZone}>
          <Text style={styles.disclaimer}>
            By continuing, you authorize read-only access to your {bankName} account data per Plaid's end-user privacy policy. Credit Clear cannot move or transfer your funds.
          </Text>
          <Pressable style={styles.button} onPress={() => router.push('/waiting-verification')}>
            <Text style={styles.buttonText}>Sign In</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 22, fontWeight: '800', color: '#1F1F3D', marginTop: 10 },
  body: { textAlign: 'center', color: '#293149', marginTop: 8, marginBottom: 16, fontSize: 13, lineHeight: 18 },
  securityBox: { borderWidth: 1, borderColor: '#36A34A', borderRadius: 8, flexDirection: 'row', gap: 12, padding: 12, alignItems: 'center', backgroundColor: '#FFF', marginBottom: 14 },
  securityIcon: { width: 28, height: 28, borderRadius: 14, backgroundColor: '#EFE2FB', justifyContent: 'center', alignItems: 'center' },
  securityTitle: { fontWeight: '800', color: '#1F1F3D' },
  securitySub: { color: '#6D7084', fontSize: 12, marginTop: 2 },
  field: { height: 48, borderRadius: 10, backgroundColor: '#F3E2FA', justifyContent: 'center', paddingHorizontal: 14, marginBottom: 12 },
  passRow: { flexDirection: 'row', alignItems: 'center' },
  input: { color: '#1F1F3D' },
  note: { color: '#6D7084', fontSize: 12, lineHeight: 18, marginBottom: 18 },
  disclaimer: { color: '#8A8A99', fontSize: 11, lineHeight: 16, textAlign: 'center', marginBottom: 14 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
});
