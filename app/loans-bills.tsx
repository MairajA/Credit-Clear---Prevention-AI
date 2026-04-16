import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

export default function LoansBillsScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Any loans or regular bills?</Text>
        <Text style={styles.body}>Optional — but the more we see, the better we protect you</Text>

        <View style={{ gap: 10, marginTop: 8 }}>
          {['Vehicle Loans', 'Student Loan', 'Mortgage', 'Phone & Utilities', 'Medical bills'].map((item) => (
            <View key={item} style={styles.row}>
              <View style={styles.icon} />
              <View style={{ flex: 1 }}>
                <Text style={styles.rowName}>{item}</Text>
                <Text style={styles.rowMeta}>
                  {item === 'Vehicle Loans'
                    ? 'Toyota Financial connected'
                    : item === 'Student Loan'
                    ? 'Navient, Nelnet, FedLoans,...'
                    : item === 'Mortgage'
                    ? 'Wells Fargo, Rocket, Mortgage...'
                    : item === 'Phone & Utilities'
                    ? 'iPhone Comcast, etc...'
                    : 'Enter outstanding balance manually'}
                </Text>
              </View>
              <Text style={styles.arrow}>→</Text>
            </View>
          ))}
        </View>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/analyzing')}>
            <Text style={styles.buttonText}>Save & continue</Text>
          </Pressable>
          <Pressable style={styles.skipButton} onPress={() => router.push('/analyzing')}>
            <Text style={styles.skipText}>Skip for now</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 21, fontWeight: '800', color: '#1F1F3D', marginTop: 10 },
  body: { textAlign: 'center', color: '#293149', marginTop: 8, fontSize: 13 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#C98BE6', backgroundColor: '#FFF' },
  icon: { width: 36, height: 36, borderRadius: 4, backgroundColor: '#EEDBF8' },
  rowName: { fontSize: 13, fontWeight: '800', color: '#1F1F3D' },
  rowMeta: { fontSize: 11, color: '#6D7084', marginTop: 2 },
  arrow: { fontSize: 18, color: '#7B4F96', fontWeight: '700', paddingHorizontal: 8 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
  skipButton: { height: 48, borderRadius: 10, backgroundColor: '#FFF', borderWidth: 1, borderColor: '#8D3F95', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  skipText: { color: '#7B4F96', fontWeight: '700' },
});
