import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

export default function ConnectedBanksScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Connected Banks</Text>
        <Text style={styles.section}>POPULAR BANKS</Text>

        <View style={{ gap: 10 }}>
          {[
            ['Chase Checking •••4521', 'Primary account', true],
            ['Chase Savings •••8834', 'Emergency Funds', false],
            ['Bank of America •••2341', 'Loans', false],
          ].map(([name, meta, selected]) => (
            <View key={String(name)} style={[styles.row, selected && styles.rowSelected]}>
              <View style={styles.icon} />
              <View style={{ flex: 1 }}>
                <Text style={styles.rowName}>{name as string}</Text>
                <Text style={styles.rowMeta}>{meta as string}</Text>
              </View>
              {selected ? <Text style={styles.check}>✓</Text> : null}
            </View>
          ))}

          <Pressable style={styles.addRow} onPress={() => router.push('/detected-cards')}>
            <Text style={styles.addPlus}>+</Text>
            <Text style={styles.addText}>Add another bank</Text>
          </Pressable>
        </View>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/detected-cards')}>
            <Text style={styles.buttonText}>Confirm & Continue</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 22, fontWeight: '800', color: '#1F1F3D', marginTop: 10, marginBottom: 18 },
  section: { fontSize: 11, color: '#7B7B8E', fontWeight: '700', marginBottom: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#C98BE6', backgroundColor: '#FFF' },
  rowSelected: { backgroundColor: '#F8ECFF' },
  icon: { width: 36, height: 36, borderRadius: 4, backgroundColor: '#EEDBF8' },
  rowName: { fontSize: 13, fontWeight: '800', color: '#1F1F3D' },
  rowMeta: { fontSize: 11, color: '#6D7084', marginTop: 2 },
  check: { fontSize: 18, color: '#662F89', fontWeight: '900', paddingHorizontal: 8 },
  addRow: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 12, borderRadius: 8, borderWidth: 1, borderStyle: 'dashed', borderColor: '#C9B9D8', backgroundColor: '#FFF' },
  addPlus: { fontSize: 26, color: '#8A4CB0', width: 32, textAlign: 'center' },
  addText: { color: '#1F1F3D', fontWeight: '700' },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
});
