import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

const steps = ['Bank accounts linked', 'Credit cards synced', 'Payment due dates mapped', 'Analyzing 12 months of transactions...', 'Calculating missed payment risk score', 'Generating your 90-day plan'];

export default function AnalyzingScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Building your credit picture...</Text>
        <Text style={styles.body}>Analyzing your accounts. This takes about 30 seconds.</Text>

        <View style={{ gap: 10, marginTop: 16 }}>
          {steps.map((step, index) => (
            <View key={step} style={[styles.step, index === steps.length - 1 && styles.activeStep]}>
              <Text style={styles.bullet}>{index < steps.length - 1 ? '✓' : '◔'}</Text>
              <Text style={styles.stepText}>{step}</Text>
            </View>
          ))}
        </View>

        <View style={styles.progressOuter}>
          <View style={styles.progressInner} />
        </View>
        <Text style={styles.complete}>Complete!</Text>

        <Text style={styles.footer}>You'll only do this setup once.</Text>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/scanned')}>
            <Text style={styles.buttonText}>View my Dashboard</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 21, fontWeight: '800', color: '#1F1F3D', marginTop: 10 },
  body: { textAlign: 'center', color: '#293149', marginTop: 8, fontSize: 13 },
  step: { minHeight: 38, borderRadius: 8, backgroundColor: '#F6F6FA', flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 12 },
  activeStep: { backgroundColor: '#F4E9FF' },
  bullet: { color: '#28A745', fontWeight: '900' },
  stepText: { color: '#293149', fontSize: 12, flex: 1 },
  progressOuter: { height: 5, borderRadius: 3, backgroundColor: '#D7B0EF', marginTop: 12, overflow: 'hidden' },
  progressInner: { width: '100%', height: 5, backgroundColor: '#662F89' },
  complete: { textAlign: 'center', color: '#8A8A99', marginTop: 6, fontSize: 12 },
  footer: { textAlign: 'center', color: '#8A8A99', marginTop: 70, fontSize: 11 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#E7E2EF', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonText: { color: '#8A8A99', fontWeight: '700', fontSize: 17 },
});
