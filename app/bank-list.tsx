import { Stack, useLocalSearchParams, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, TextInput, View, ScrollView } from 'react-native';
import { useMemo, useState } from 'react';

import AuthLayout from '@/components/auth/AuthLayout';

const ALL_BANKS = [
  'Chase', 'Wells Fargo', 'Bank of America', 'Citibank', 'US Bank', 'Capital One', 'PNC Bank', 'Truist',
  'TD Bank', 'Huntington', 'KeyBank', 'M&T Bank', 'Regions', 'Fifth Third Bank', 'U.S. Bank', 'BB&T',
  'Ally Bank', 'Chime', 'SoFi', 'Discover', 'Charles Schwab', 'American Express', 'Navy Federal', 'USAA',
];

export default function BankListScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ selected?: string }>();
  const [query, setQuery] = useState('');

  const filteredBanks = useMemo(() => {
    const q = query.trim().toLowerCase();
    return ALL_BANKS.filter((bank) => bank.toLowerCase().includes(q));
  }, [query]);

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Pressable onPress={() => router.back()}>
          <Text style={styles.back}>Back</Text>
        </Pressable>

        <Text style={styles.title}>Choose a bank</Text>
        <Text style={styles.body}>Select from the full list and continue to connect it.</Text>

        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>⌕</Text>
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search banks"
            placeholderTextColor="#9B8BB0"
            style={styles.searchInput}
          />
        </View>

        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 20 }}>
          <View style={{ gap: 10 }}>
            {filteredBanks.map((bank) => (
              <Pressable
                key={bank}
                style={styles.row}
                onPress={() => router.push({ pathname: '/connect-bank', params: { selected: bank } })}>
                <View style={styles.icon} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.rowName}>{bank}</Text>
                  <Text style={styles.rowMeta}>Checking, Savings, Credit</Text>
                </View>
                {params.selected === bank ? <Text style={styles.check}>✓</Text> : null}
              </Pressable>
            ))}
          </View>
        </ScrollView>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  back: { color: '#1F1F3D', fontSize: 15, marginTop: 4, marginBottom: 8 },
  title: { textAlign: 'center', fontSize: 22, fontWeight: '800', color: '#1F1F3D', marginBottom: 8 },
  body: { textAlign: 'center', color: '#293149', marginBottom: 14, fontSize: 13 },
  searchBox: { height: 48, borderRadius: 10, backgroundColor: '#F3E2FA', flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, marginBottom: 14 },
  searchIcon: { fontSize: 22, color: '#7C3AED', marginRight: 10 },
  searchInput: { flex: 1, height: 48, color: '#1F1F3D' },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#C98BE6', backgroundColor: '#FFF' },
  icon: { width: 36, height: 36, borderRadius: 4, backgroundColor: '#EEDBF8' },
  rowName: { fontSize: 14, fontWeight: '800', color: '#1F1F3D' },
  rowMeta: { fontSize: 11, color: '#6D7084', marginTop: 2 },
  check: { fontSize: 18, color: '#662F89', fontWeight: '900', paddingHorizontal: 8 },
});
