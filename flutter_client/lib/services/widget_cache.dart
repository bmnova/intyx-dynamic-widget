/// Local cache for widget responses.
///
/// Uses SharedPreferences to persist the last-known-good API response for
/// each cache key. The cache is a pure network-failure fallback: it is
/// written on every successful fetch and read only when the network call
/// throws. Stale data is always preferred over an empty screen.
library;

import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/widget_response.dart';

class WidgetCache {
  static const _prefix = 'intyx_widget_cache_';

  /// Persists a raw API response body string under [key].
  Future<void> save(String key, String rawJson) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('$_prefix$key', rawJson);
  }

  /// Returns the cached widget list for [key], or `null` if nothing is stored
  /// or the stored data cannot be parsed.
  Future<List<WidgetEntry>?> load(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('$_prefix$key');
    if (raw == null) return null;
    try {
      final data = json.decode(raw) as Map<String, dynamic>;
      return WidgetResponse.fromJson(data).widgets;
    } catch (_) {
      return null;
    }
  }

  /// Removes the cached entry for [key].
  Future<void> clear(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('$_prefix$key');
  }

  /// Removes all entries written by this cache.
  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = prefs.getKeys().where((k) => k.startsWith(_prefix)).toList();
    for (final k in keys) {
      await prefs.remove(k);
    }
  }
}
