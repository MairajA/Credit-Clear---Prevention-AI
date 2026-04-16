import { Stack, useLocalSearchParams, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useEffect, useState } from 'react';

import AuthLayout from '@/components/auth/AuthLayout';

const banks = ['Chase', 'Wells Fargo', 'Bank of America', 'Citibank', 'US Bank'];

export default function ConnectBankScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ selected?: string }>();
  const [selected, setSelected] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (typeof params.selected === 'string') {
      setSelected(params.selected);
    }
  }, [params.selected]);

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <AuthLayout>
        <Text style={styles.title}>Start with your main bank</Text>
        <Text style={styles.body}>We track your cash flow and predict shortfalls here</Text>

        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>⌕</Text>
          <TextInput placeholder="Search your Bank" placeholderTextColor="#9B8BB0" value={search} onChangeText={setSearch} style={styles.searchInput} />
        </View>

        <Text style={styles.section}>POPULAR BANKS</Text>
        <View style={{ gap: 10 }}>
          {banks.map((bank) => {
            const isSelected = selected === bank;
            return (
              <Pressable key={bank} style={[styles.bankRow, isSelected && styles.bankRowSelected]} onPress={() => setSelected(bank)}>
                <View style={styles.bankIcon} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.bankName}>{bank}</Text>
                  <Text style={styles.bankMeta}>Checking, Savings, Credit</Text>
                </View>
                {isSelected ? <Text style={styles.check}>✓</Text> : null}
              </Pressable>
            );
          })}
        </View>

        <Pressable style={styles.moreBanksWrap} onPress={() => router.push('/bank-list')}>
          <Text style={styles.moreBanks}>+ see all 12,000 banks</Text>
        </Pressable>

        <View style={styles.bottomZone}>
          <Pressable
            style={[styles.button, !selected && styles.buttonDisabled]}
            onPress={() => router.push({ pathname: '/sign-in-bank', params: { bank: selected } })}
            disabled={!selected}>
            <Text style={styles.buttonText}>{selected ? `Connect to ${selected}` : 'Select Bank to Proceed'}</Text>
          </Pressable>
        </View>
      </AuthLayout>
    </>
  );
}

const styles = StyleSheet.create({
  title: { textAlign: 'center', fontSize: 21, fontWeight: '800', color: '#1F1F3D', marginTop: 10 },
  body: { textAlign: 'center', color: '#293149', marginTop: 8, marginBottom: 18, fontSize: 13 },
  searchBox: { height: 48, borderRadius: 10, backgroundColor: '#F3E2FA', flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, marginBottom: 14 },
  searchIcon: { fontSize: 22, color: '#7C3AED', marginRight: 10 },
  searchInput: { flex: 1, height: 48, color: '#1F1F3D' },
  section: { fontSize: 11, color: '#7B7B8E', fontWeight: '700', marginBottom: 8 },
  bankRow: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#C98BE6', backgroundColor: '#FFF' },
  bankRowSelected: { backgroundColor: '#F8ECFF' },
  bankIcon: { width: 36, height: 36, borderRadius: 4, backgroundColor: '#EEDBF8' },
  bankName: { fontSize: 14, fontWeight: '800', color: '#1F1F3D' },
  bankMeta: { fontSize: 11, color: '#6D7084', marginTop: 2 },
  check: { fontSize: 18, color: '#662F89', fontWeight: '900', paddingHorizontal: 8 },
  moreBanksWrap: { alignSelf: 'center', marginTop: 14 },
  moreBanks: { textAlign: 'center', color: '#9B68C7', marginTop: 14, fontSize: 13 },
  bottomZone: { flex: 1, justifyContent: 'flex-end' },
  button: { height: 52, borderRadius: 10, backgroundColor: '#662F89', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  buttonDisabled: { opacity: 0.45 },
  buttonText: { color: '#FFF', fontWeight: '700', fontSize: 17 },
});
