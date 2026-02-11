/// Firebase Firestore service for realtime widget updates.
library;

import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';

import '../models/widget_response.dart';

class FirebaseWidgetService {
  final FirebaseFirestore _firestore;

  FirebaseWidgetService({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  /// Stream of widget entries from Firestore, sorted by priority.
  Stream<List<WidgetEntry>> watchWidgets() {
    return _firestore
        .collection('widgets')
        .orderBy('priority', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        final data = doc.data();
        data['id'] = doc.id;
        return WidgetEntry(
          id: doc.id,
          type: data['type'] as String? ?? '',
          params: data['params'] as Map<String, dynamic>? ?? {},
          common: data['common'] != null
              ? CommonParams.fromJson(data['common'] as Map<String, dynamic>)
              : const CommonParams(),
        );
      }).toList();
    });
  }

  /// Stream of user state (dismissed widgets).
  Stream<Set<String>> watchDismissedWidgets(String userId) {
    return _firestore
        .collection('user_states')
        .doc(userId)
        .snapshots()
        .map((snapshot) {
      if (!snapshot.exists) return <String>{};
      final data = snapshot.data() ?? {};
      final dismissed = data['dismissed_widgets'] as List<dynamic>? ?? [];
      return dismissed.map((e) => e.toString()).toSet();
    });
  }

  /// Dismiss a widget for a user.
  Future<void> dismissWidget(String userId, String widgetId) async {
    final docRef = _firestore.collection('user_states').doc(userId);
    await _firestore.runTransaction((tx) async {
      final doc = await tx.get(docRef);
      if (doc.exists) {
        final dismissed = List<String>.from(
          doc.data()?['dismissed_widgets'] as List<dynamic>? ?? [],
        );
        if (!dismissed.contains(widgetId)) {
          dismissed.add(widgetId);
          tx.update(docRef, {'dismissed_widgets': dismissed});
        }
      } else {
        tx.set(docRef, {
          'dismissed_widgets': [widgetId],
          'actions': [],
        });
      }
    });
  }

  /// Record an interaction.
  Future<void> recordInteraction(
    String userId,
    String widgetId,
    String action,
  ) async {
    final docRef = _firestore.collection('user_states').doc(userId);
    await docRef.set({
      'actions': FieldValue.arrayUnion([
        {
          'widget_id': widgetId,
          'action': action,
          'timestamp': FieldValue.serverTimestamp(),
        }
      ]),
    }, SetOptions(merge: true));
  }
}
