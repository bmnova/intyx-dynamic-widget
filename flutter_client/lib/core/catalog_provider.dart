/// Provides the widget catalog JSON for sending to the AI agent.
library;

import 'dart:convert';

import 'package:flutter/services.dart';

class CatalogProvider {
  CatalogProvider._();

  static Map<String, dynamic>? _catalog;

  /// Load the catalog from the bundled asset.
  static Future<Map<String, dynamic>> loadCatalog() async {
    if (_catalog != null) return _catalog!;

    final jsonStr = await rootBundle.loadString(
      'packages/intyx_dynamic_widget/catalog/widget_catalog.json',
    );
    _catalog = json.decode(jsonStr) as Map<String, dynamic>;
    return _catalog!;
  }

  /// Get the catalog synchronously (must call loadCatalog first).
  static Map<String, dynamic>? getCatalog() => _catalog;

  /// Get the catalog as a JSON string for sending to the agent.
  static String? getCatalogJson() {
    if (_catalog == null) return null;
    return json.encode(_catalog);
  }

  /// Get available widget types from the catalog.
  static List<String> getWidgetTypes() {
    if (_catalog == null) return [];
    final widgets = _catalog!['widgets'] as List<dynamic>? ?? [];
    return widgets
        .map((w) => (w as Map<String, dynamic>)['type'] as String)
        .toList();
  }
}
