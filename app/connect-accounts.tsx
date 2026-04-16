import { Stack, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import AuthLayout from '@/components/auth/AuthLayout';

const items = [
  ['MONITOR', 'Every account in one place — balances, limits, due dates'],
  ['PREDICT', 'Catch payment risks 7 days before they happen'],
  ['PROTECT', 'We act with creditors before your score takes a hit'],
];

export default function ConnectAccountsScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Let's protect your credit.</Text>
        <Text style={styles.body}>
          Before we build your plan, we need to see the full picture. Connect your accounts, it takes under 2 minutes.
        </Text>

        <View style={styles.cards}>
          {items.map(([title, description]) => (
            <View key={title} style={styles.card}>
              <View style={styles.iconBox} />
              <View style={styles.cardText}>
                <Text style={styles.cardTitle}>{title}</Text>
                <Text style={styles.cardDesc}>{description}</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={styles.bottomZone}>
          <Pressable style={styles.button} onPress={() => router.push('/connect-bank')}>
            <Text style={styles.buttonText}>Connect my account</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: {
    textAlign: 'center',
    fontSize: 22,
    fontWeight: '800',
    color: '#1F1F3D',
    marginTop: 10,
    marginBottom: 10,
  },
  body: {
    textAlign: 'center',
    color: '#293149',
    fontSize: 14,
    lineHeight: 20,
    paddingHorizontal: 8,
    marginBottom: 22,
  },
  cards: { gap: 12 },
  card: {
    borderWidth: 1,
    borderColor: '#A56AD3',
    borderRadius: 8,
    backgroundColor: '#FFF',
    flexDirection: 'row',
    padding: 12,
    alignItems: 'center',
  },
  iconBox: {
    width: 46,
    height: 46,
    borderRadius: 6,
    backgroundColor: '#F1E5F9',
    marginRight: 12,
  },
  cardText: { flex: 1 },
  cardTitle: { fontSize: 16, fontWeight: '800', color: '#1F1F3D', marginBottom: 3 },
  cardDesc: { fontSize: 12, color: '#666A80', lineHeight: 16 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: {
    height: 52,
    borderRadius: 10,
    backgroundColor: '#662F89',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 18 },
});
