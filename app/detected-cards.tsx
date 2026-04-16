import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

export default function DetectedCardsScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Now add your credit cards</Text>
        <Text style={styles.body}>We track utilization, due dates & balances to prevent missed payments</Text>

        <View style={styles.notice}><Text style={styles.noticeText}>◻ 2 cards detected from your Chase connection</Text></View>

        <View style={{ gap: 10 }}>
          {[
            ['Amex Gold **3041', '$4,000 limit', 'Balance $1050', 'due in 3 days'],
            ['Discover it **7121', '$2,500 limit', 'Balance $500', 'due in 3 days'],
          ].map(([name, limit, balance, due]) => (
            <View key={String(name)} style={styles.row}>
              <View style={styles.icon} />
              <View style={{ flex: 1 }}>
                <Text style={styles.rowName}>{name as string}</Text>
                <Text style={styles.rowMeta}>{limit as string}  |  {balance as string}</Text>
                <Text style={styles.due}>{due as string}</Text>
              </View>
              <Text style={styles.check}>✓</Text>
            </View>
          ))}
          <Pressable style={styles.addRow} onPress={() => router.push('/loans-bills')}>
            <Text style={styles.addPlus}>+</Text>
            <Text style={styles.addText}>Add Card manually</Text>
          </Pressable>
        </View>

        <Text style={styles.muted}>Missing a card? Add more anytime from Settings.</Text>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/loans-bills')}>
            <Text style={styles.buttonText}>Confirm Cards</Text>
          </Pressable>
          <Pressable style={styles.skipButton} onPress={() => router.push('/loans-bills')}>
            <Text style={styles.skipText}>Skip for now</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 21, fontWeight: '800', color: '#1F1F3D', marginTop: 10 },
  body: { textAlign: 'center', color: '#293149', marginTop: 8, marginBottom: 14, fontSize: 13, lineHeight: 18 },
  notice: { backgroundColor: '#F7E4C2', padding: 10, borderRadius: 8, marginBottom: 12, alignItems: 'center' },
  noticeText: { fontSize: 12, color: '#8E5C00', fontWeight: '700' },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#C98BE6', backgroundColor: '#FFF' },
  icon: { width: 36, height: 36, borderRadius: 4, backgroundColor: '#EEDBF8' },
  rowName: { fontSize: 13, fontWeight: '800', color: '#1F1F3D' },
  rowMeta: { fontSize: 11, color: '#6D7084', marginTop: 2 },
  due: { fontSize: 11, color: '#D0342C', fontWeight: '700', marginTop: 4 },
  check: { fontSize: 18, color: '#662F89', fontWeight: '900', paddingHorizontal: 8 },
  addRow: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 12, borderRadius: 8, borderWidth: 1, borderStyle: 'dashed', borderColor: '#C9B9D8', backgroundColor: '#FFF' },
  addPlus: { fontSize: 26, color: '#8A4CB0', width: 32, textAlign: 'center' },
  addText: { color: '#1F1F3D', fontWeight: '700' },
  muted: { textAlign: 'center', color: '#9B9BA7', fontSize: 11, marginTop: 10 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
  skipButton: { height: 48, borderRadius: 10, backgroundColor: '#FFF', borderWidth: 1, borderColor: '#8D3F95', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  skipText: { color: '#7B4F96', fontWeight: '700' },
});
