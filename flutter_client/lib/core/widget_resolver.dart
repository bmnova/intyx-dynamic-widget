/// Resolves agent JSON response into a list of Flutter widgets.
library;

import 'package:flutter/widgets.dart';

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
    OnWidgetDismiss? onDismiss,
    OnWidgetAction? onAction,
  }) {
    final response = WidgetResponse.fromJson(responseJson);
    return resolveEntries(
      response.widgets,
      onDismiss: onDismiss,
      onAction: onAction,
    );
  }

  /// Resolve a list of WidgetEntry into Flutter widgets.
  static List<Widget> resolveEntries(
    List<WidgetEntry> entries, {
    OnWidgetDismiss? onDismiss,
    OnWidgetAction? onAction,
  }) {
    final widgets = <Widget>[];

    for (final entry in entries) {
      final child = WidgetRegistry.build(entry.type, entry.params);
      if (child == null) continue;

      Widget wrapped = ResponsiveWidgetWrapper(
        layout: entry.common.layout,
        themeOverride: entry.common.themeOverride,
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
  static Widget? resolveSingle(WidgetEntry entry) {
    final child = WidgetRegistry.build(entry.type, entry.params);
    if (child == null) return null;

    return ResponsiveWidgetWrapper(
      layout: entry.common.layout,
      themeOverride: entry.common.themeOverride,
      child: child,
    );
  }
}
