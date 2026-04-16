import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

export default function PaymentsScreen() {
  const payments = [
    {
      id: 1,
      name: 'Credit Card Payment',
      amount: '$120.00',
      dueDate: 'Due in 5 days',
      status: 'upcoming',
      icon: '💳',
    },
    {
      id: 2,
      name: 'Electricity Bill',
      amount: '$85.50',
      dueDate: 'Due in 12 days',
      status: 'upcoming',
      icon: '⚡',
    },
    {
      id: 3,
      name: 'Internet Bill',
      amount: '$60.00',
      dueDate: 'Paid on Apr 10',
      status: 'paid',
      icon: '📡',
    },
    {
      id: 4,
      name: 'Car Payment',
      amount: '$350.00',
      dueDate: 'Paid on Apr 5',
      status: 'paid',
      icon: '🚗',
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Payments</Text>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsRow}>
        <View style={[styles.statCard, { backgroundColor: '#FFF3E0' }]}>
          <Text style={styles.statLabel}>Total Due</Text>
          <Text style={styles.statValue}>$205.50</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: '#E8F5E9' }]}>
          <Text style={styles.statLabel}>0 Missed</Text>
          <Text style={styles.statValue}>100%</Text>
        </View>
      </View>

      {/* Upcoming Payments */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Upcoming</Text>
        {payments
          .filter((p) => p.status === 'upcoming')
          .map((payment) => (
            <View key={payment.id} style={styles.paymentCard}>
              <View style={styles.paymentHeader}>
                <Text style={styles.paymentIcon}>{payment.icon}</Text>
                <View style={styles.paymentDetails}>
                  <Text style={styles.paymentName}>{payment.name}</Text>
                  <Text style={styles.paymentDue}>{payment.dueDate}</Text>
                </View>
              </View>
              <TouchableOpacity style={styles.payButton}>
                <Text style={styles.payButtonText}>{payment.amount}</Text>
              </TouchableOpacity>
            </View>
          ))}
      </View>

      {/* Paid Payments */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Paid This Month</Text>
        {payments
          .filter((p) => p.status === 'paid')
          .map((payment) => (
            <View key={payment.id} style={[styles.paymentCard, styles.paidCard]}>
              <View style={styles.paymentHeader}>
                <Text style={styles.paymentIcon}>{payment.icon}</Text>
                <View style={styles.paymentDetails}>
                  <Text style={[styles.paymentName, styles.paidText]}>
                    {payment.name}
                  </Text>
                  <Text style={styles.paymentDue}>{payment.dueDate}</Text>
                </View>
              </View>
              <Text style={[styles.paidAmount, styles.paidText]}>{payment.amount}</Text>
            </View>
          ))}
      </View>

      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F3FF',
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    borderRadius: 12,
    padding: 16,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1F1F3D',
    marginBottom: 12,
  },
  paymentCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  paidCard: {
    opacity: 0.6,
  },
  paymentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  paymentIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  paymentDetails: {
    flex: 1,
  },
  paymentName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F1F3D',
  },
  paidText: {
    color: '#999',
  },
  paymentDue: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  payButton: {
    backgroundColor: '#7C3AED',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  payButtonText: {
    color: '#FFF',
    fontWeight: '600',
    fontSize: 12,
  },
  paidAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: '#7C3AED',
  },
});
