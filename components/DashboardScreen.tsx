import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export default function DashboardScreen() {
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>Hello, User</Text>
        <TouchableOpacity style={styles.settingsIcon}>
          <Text style={styles.settingsText}>⚙️</Text>
        </TouchableOpacity>
      </View>

      {/* Credit Score Card */}
      <LinearGradient colors={['#7C3AED', '#EC4899']} style={styles.creditCard}>
        <Text style={styles.cardLabel}>Your Credit Score</Text>
        <Text style={styles.creditScore}>720</Text>
        <Text style={styles.creditStatus}>Good • +18 this month</Text>
      </LinearGradient>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={[styles.statBox, { backgroundColor: '#E8F5E9' }]}>
          <Text style={styles.statValue}>0%</Text>
          <Text style={styles.statLabel}>Missed Payments</Text>
        </View>
        <View style={[styles.statBox, { backgroundColor: '#FFF3E0' }]}>
          <Text style={styles.statValue}>28%</Text>
          <Text style={styles.statLabel}>Credit Utilization</Text>
        </View>
      </View>

      {/* 90-Day Roadmap Preview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>90-Day Roadmap</Text>
        <View style={styles.roadmapBox}>
          <View style={styles.roadmapItem}>
            <View style={[styles.roadmapStep, { backgroundColor: '#7C3AED' }]} />
            <Text style={styles.roadmapLabel}>Days 1-30</Text>
            <Text style={styles.roadmapDesc}>Fix errors</Text>
          </View>
          <View style={styles.roadmapItem}>
            <View style={[styles.roadmapStep, { backgroundColor: '#E0D4F7' }]} />
            <Text style={styles.roadmapLabel}>Days 31-60</Text>
            <Text style={styles.roadmapDesc}>Build history</Text>
          </View>
          <View style={styles.roadmapItem}>
            <View style={[styles.roadmapStep, { backgroundColor: '#E0D4F7' }]} />
            <Text style={styles.roadmapLabel}>Days 61-90</Text>
            <Text style={styles.roadmapDesc}>Optimize</Text>
          </View>
        </View>
      </View>

      {/* Upcoming Payments */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Upcoming Payments</Text>
          <TouchableOpacity>
            <Text style={styles.seeAll}>See all</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.paymentItem}>
          <Text style={styles.paymentIcon}>💳</Text>
          <View style={styles.paymentInfo}>
            <Text style={styles.paymentName}>Credit Card Payment</Text>
            <Text style={styles.paymentDate}>Due in 5 days</Text>
          </View>
          <Text style={styles.paymentAmount}>$120.00</Text>
        </View>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  settingsIcon: {
    padding: 8,
  },
  settingsText: {
    fontSize: 24,
  },
  creditCard: {
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
  },
  cardLabel: {
    fontSize: 12,
    color: '#FFF',
    opacity: 0.8,
    marginBottom: 8,
  },
  creditScore: {
    fontSize: 48,
    fontWeight: '700',
    color: '#FFF',
    marginBottom: 8,
  },
  creditStatus: {
    fontSize: 14,
    color: '#FFF',
    opacity: 0.9,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statBox: {
    flex: 1,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1F1F3D',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  seeAll: {
    fontSize: 14,
    color: '#7C3AED',
    fontWeight: '600',
  },
  roadmapBox: {
    flexDirection: 'row',
    gap: 8,
  },
  roadmapItem: {
    flex: 1,
    alignItems: 'center',
  },
  roadmapStep: {
    width: 40,
    height: 40,
    borderRadius: 8,
    marginBottom: 8,
  },
  roadmapLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#1F1F3D',
    marginBottom: 2,
  },
  roadmapDesc: {
    fontSize: 10,
    color: '#999',
  },
  paymentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 12,
    gap: 12,
  },
  paymentIcon: {
    fontSize: 24,
  },
  paymentInfo: {
    flex: 1,
  },
  paymentName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F1F3D',
  },
  paymentDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  paymentAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: '#EC4899',
  },
});
