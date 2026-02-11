/// Resolves agent JSON response into a list of Flutter widgets.
library;

import 'package:flutter/material.dart';

import '../models/widget_response.dart';
import 'responsive_widget_wrapper.dart';
import 'widget_registry.dart';

/// Callbacks for widget events.
typedef OnWidgetDismiss = void Function(String widgetId);
typedef OnWidgetAction = void Function(String widgetId, String action);

class WidgetResolver {
  WidgetResolver._();

  /// Resolve a full agent JSON response into Flutter widgets.
  static List<Widget> resolve(
    Map<String, dynamic> responseJson, {
    ColorScheme? hostColorScheme,
    OnWidgetDismiss? onDismiss,
    OnWidgetAction? onAction,
  }) {
    final response = WidgetResponse.fromJson(responseJson);
    return resolveEntries(
      response.widgets,
      hostColorScheme: hostColorScheme,
      onDismiss: onDismiss,
      onAction: onAction,
    );
  }

  /// Resolve a list of WidgetEntry into Flutter widgets.
  ///
  /// Priority for ColorScheme (highest wins):
  ///   1. Per-widget `color_palette` from agent JSON
  ///   2. [hostColorScheme] passed by the developer
  ///   3. The ambient Theme from context
  static List<Widget> resolveEntries(
    List<WidgetEntry> entries, {
    ColorScheme? hostColorScheme,
    OnWidgetDismiss? onDismiss,
    OnWidgetAction? onAction,
  }) {
    final widgets = <Widget>[];

    for (final entry in entries) {
      final child = WidgetRegistry.build(entry.type, entry.params);
      if (child == null) continue;

      // Per-widget color scheme from agent JSON takes priority,
      // then the host's color scheme passed by the developer.
      final effectiveColorScheme =
          entry.common.colorScheme ?? hostColorScheme;

      Widget wrapped = ResponsiveWidgetWrapper(
        layout: entry.common.layout,
        themeOverride: entry.common.themeOverride,
        colorScheme: effectiveColorScheme,
        child: child,
      );

      if (entry.common.dismissible && onDismiss != null) {
        wrapped = Dismissible(
          key: ValueKey(entry.id),
          onDismissed: (_) => onDismiss(entry.id),
          child: wrapped,
        );
      }

      widgets.add(wrapped);
    }

    return widgets;
  }

  /// Resolve a single widget entry.
  static Widget? resolveSingle(
    WidgetEntry entry, {
    ColorScheme? hostColorScheme,
  }) {
    final child = WidgetRegistry.build(entry.type, entry.params);
    if (child == null) return null;

    final effectiveColorScheme =
        entry.common.colorScheme ?? hostColorScheme;

    return ResponsiveWidgetWrapper(
      layout: entry.common.layout,
      themeOverride: entry.common.themeOverride,
      colorScheme: effectiveColorScheme,
      child: child,
    );
  }
}
