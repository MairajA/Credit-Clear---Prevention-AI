import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import AuthLayout from '@/components/auth/AuthLayout';

export default function ScannedScreen() {
  const router = useRouter();

  const rows = [
    ['Payments at risk', 'Amex Gold due in 3 days — low balance detected', '2 found'],
    ['Credit errors detected', 'Potential disputes across Equifax & TransUnion', '3 items'],
    ['Estimated score boost', 'Based on disputes, utilization, and payment history', '+52-74 pts'],
  ] as const;

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <View style={styles.iconWrap}>
          <Ionicons name="shield-checkmark" size={52} color="#662F89" />
        </View>
        <Text style={styles.title}>You're protected.</Text>
        <Text style={styles.body}>Here's what we found across your connected accounts.</Text>

        <View style={{ gap: 10, marginTop: 16 }}>
          {rows.map(([title, body, badge]) => (
            <View key={title} style={styles.row}>
              <View style={styles.icon} />
              <View style={{ flex: 1 }}>
                <Text style={styles.rowTitle}>{title}</Text>
                <Text style={styles.rowBody}>{body}</Text>
              </View>
              <View style={styles.badge}><Text style={styles.badgeText}>{badge}</Text></View>
            </View>
          ))}
        </View>

        <Text style={styles.footer}>Credit Clear is now monitoring your accounts 24/7. We'll alert you before anything goes wrong.</Text>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.replace('/(tabs)')}>
            <Text style={styles.buttonText}>View my Dashboard</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  iconWrap: { alignItems: 'center', justifyContent: 'center', marginTop: 30, marginBottom: 8 },
  title: { textAlign: 'center', fontSize: 22, fontWeight: '800', color: '#1F1F3D', marginTop: 8 },
  body: { textAlign: 'center', color: '#293149', marginTop: 8, fontSize: 13 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#C98BE6', backgroundColor: '#FFF' },
  icon: { width: 36, height: 36, borderRadius: 4, backgroundColor: '#EEDBF8' },
  rowTitle: { fontSize: 13, fontWeight: '800', color: '#1F1F3D' },
  rowBody: { fontSize: 11, color: '#6D7084', marginTop: 2 },
  badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, backgroundColor: '#F2E8FF' },
  badgeText: { color: '#662F89', fontWeight: '700', fontSize: 11 },
  footer: { textAlign: 'center', color: '#8A8A99', fontSize: 11, lineHeight: 16, marginTop: 12 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
});
