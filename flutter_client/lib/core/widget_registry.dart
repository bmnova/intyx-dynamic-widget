/// Registry that maps widget type strings to Flutter widget builders.
library;

import 'package:flutter/widgets.dart';

/// Signature for a factory that builds a widget from JSON params.
/// [onAction] is called when the widget triggers an action (e.g. button tap,
/// link tap) and receives the target URL or action string.
typedef WidgetBuilder = Widget Function(
  Map<String, dynamic> params, {
  void Function(String url)? onAction,
});

class WidgetRegistry {
  WidgetRegistry._();

  static final Map<String, WidgetBuilder> _builders = {};

  /// Register a widget builder for a given type.
  static void register(String type, WidgetBuilder builder) {
    _builders[type] = builder;
  }

  /// Register multiple builders at once.
  static void registerAll(Map<String, WidgetBuilder> builders) {
    _builders.addAll(builders);
  }

  /// Build a widget for the given type and params.
  /// Returns null if the type is not registered.
  static Widget? build(
    String type,
    Map<String, dynamic> params, {
    void Function(String url)? onAction,
  }) {
    final builder = _builders[type];
    if (builder == null) return null;
    return builder(params, onAction: onAction);
  }

  /// Check if a type is registered.
  static bool hasType(String type) => _builders.containsKey(type);

  /// Get all registered type names.
  static Set<String> get registeredTypes => _builders.keys.toSet();

  /// Clear all registrations (useful for testing).
  static void clear() => _builders.clear();
}
