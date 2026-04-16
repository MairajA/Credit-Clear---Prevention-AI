import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function BudgetScreen() {
  const expenses = [
    { id: 1, category: 'Housing', amount: 1200, icon: '🏠', percentage: 35 },
    { id: 2, category: 'Food', amount: 400, icon: '🍔', percentage: 12 },
    { id: 3, category: 'Transportation', amount: 350, icon: '🚗', percentage: 10 },
    { id: 4, category: 'Utilities', amount: 200, icon: '⚡', percentage: 6 },
    { id: 5, category: 'Entertainment', amount: 300, icon: '🎬', percentage: 8 },
    { id: 6, category: 'Other', amount: 700, icon: '📦', percentage: 29 },
  ];

  const monthlyBudget = 3150;
  const remaining = 342.76;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Budget & Expenses</Text>
      </View>

      {/* Budget Overview */}
      <View style={styles.overviewCard}>
        <View style={styles.overviewRow}>
          <View>
            <Text style={styles.overviewLabel}>Monthly Budget</Text>
            <Text style={styles.overviewValue}>${monthlyBudget.toLocaleString()}</Text>
          </View>
          <View style={styles.divider} />
          <View>
            <Text style={styles.overviewLabel}>Remaining</Text>
            <Text style={[styles.overviewValue, { color: '#4CAF50' }]}>
              ${remaining.toLocaleString()}
            </Text>
          </View>
        </View>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              {
                width: `${((monthlyBudget - remaining) / monthlyBudget) * 100}%`,
              },
            ]}
          />
        </View>
        <Text style={styles.progressText}>
          {(((monthlyBudget - remaining) / monthlyBudget) * 100).toFixed(0)}% spent
        </Text>
      </View>

      {/* Category Breakdown */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Spending by Category</Text>
        {expenses.map((expense) => (
          <View key={expense.id} style={styles.categoryItem}>
            <View style={styles.categoryInfo}>
              <Text style={styles.categoryIcon}>{expense.icon}</Text>
              <View>
                <Text style={styles.categoryName}>{expense.category}</Text>
                <Text style={styles.categoryAmount}>${expense.amount}</Text>
              </View>
            </View>
            <View style={styles.categoryBar}>
              <View
                style={[
                  styles.categoryBarFill,
                  { width: `${expense.percentage}%` },
                ]}
              />
            </View>
            <Text style={styles.categoryPercent}>{expense.percentage}%</Text>
          </View>
        ))}
      </View>

      {/* Insights */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tips</Text>
        <View style={styles.tipsBox}>
          <Text style={styles.tipIcon}>💡</Text>
          <View>
            <Text style={styles.tipText}>You're spending 8% more on food this month.</Text>
            <Text style={styles.tipSubtext}>Try meal planning to save $50/month</Text>
          </View>
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
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  overviewCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
  },
  overviewRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  overviewLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  overviewValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1F1F3D',
  },
  divider: {
    width: 1,
    height: 40,
    backgroundColor: '#E0D4F7',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0D4F7',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#7C3AED',
  },
  progressText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F1F3D',
    marginBottom: 12,
  },
  categoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 12,
  },
  categoryInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    width: 100,
  },
  categoryIcon: {
    fontSize: 24,
  },
  categoryName: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F1F3D',
  },
  categoryAmount: {
    fontSize: 11,
    color: '#999',
    marginTop: 2,
  },
  categoryBar: {
    flex: 1,
    height: 6,
    backgroundColor: '#E0D4F7',
    borderRadius: 3,
    marginHorizontal: 12,
    overflow: 'hidden',
  },
  categoryBarFill: {
    height: '100%',
    backgroundColor: '#7C3AED',
  },
  categoryPercent: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F1F3D',
    width: 35,
    textAlign: 'right',
  },
  tipsBox: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: 14,
    flexDirection: 'row',
    gap: 12,
  },
  tipIcon: {
    fontSize: 24,
  },
  tipText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F1F3D',
  },
  tipSubtext: {
    fontSize: 11,
    color: '#666',
    marginTop: 4,
  },
});
