import 'package:flutter/material.dart';

import '../core/widget_resolver.dart';
import '../models/widget_response.dart';
import '../services/widget_service.dart';

/// Main container that renders a list of widgets from agent JSON response.
///
/// Developer places this widget in the app and optionally passes the host
/// app's [ColorScheme] so that dynamic widgets blend with the host design.
///
/// ```dart
/// DynamicWidgetContainer(
///   responseJson: agentResponse,
///   colorScheme: Theme.of(context).colorScheme,
///   padding: EdgeInsets.all(12),
/// )
/// ```
class DynamicWidgetContainer extends StatelessWidget {
  /// Agent response JSON containing widgets array.
  final Map<String, dynamic>? responseJson;

  /// Pre-parsed widget entries (alternative to responseJson).
  final List<WidgetEntry>? entries;

  /// Host app's color scheme. When provided, widgets render using these
  /// colors instead of the default theme. This is the primary way for
  /// developers to make dynamic widgets match their app's look and feel.
  final ColorScheme? colorScheme;

  /// Called when a widget is dismissed.
  final OnWidgetDismiss? onDismiss;

  /// Called when a widget action is triggered.
  final OnWidgetAction? onAction;

  /// User ID for automatic analytics tracking.
  ///
  /// When provided together with [analyticsService], the SDK will
  /// automatically record `impression`, `dismiss`, and `action` events
  /// without any extra work from the developer.
  final String? userId;

  /// Service instance used for automatic analytics tracking.
  ///
  /// Must be provided together with [userId] to enable auto-tracking.
  final WidgetService? analyticsService;

  /// Spacing between widgets.
  final double spacing;

  /// Padding around the widget list.
  final EdgeInsetsGeometry padding;

  /// Whether to use a scrollable list.
  final bool scrollable;

  const DynamicWidgetContainer({
    super.key,
    this.responseJson,
    this.entries,
    this.colorScheme,
    this.onDismiss,
    this.onAction,
    this.userId,
    this.analyticsService,
    this.spacing = 8,
    this.padding = const EdgeInsets.all(16),
    this.scrollable = true,
  }) : assert(
          responseJson != null || entries != null,
          'Either responseJson or entries must be provided',
        );

  @override
  Widget build(BuildContext context) {
    // When analytics is configured, wrap onAction to also record the event.
    OnWidgetAction? effectiveAction = onAction;
    if (userId != null && analyticsService != null && onAction != null) {
      effectiveAction = (id, action) {
        analyticsService!
            .recordInteraction(id, userId!, action: action)
            .ignore();
        onAction!(id, action);
      };
    }

    final List<Widget> widgets;

    if (entries != null) {
      widgets = WidgetResolver.resolveEntries(
        entries!,
        hostColorScheme: colorScheme,
        onDismiss: onDismiss,
        onAction: effectiveAction,
        userId: userId,
        analyticsService: analyticsService,
      );
    } else {
      widgets = WidgetResolver.resolve(
        responseJson!,
        hostColorScheme: colorScheme,
        onDismiss: onDismiss,
        onAction: effectiveAction,
        userId: userId,
        analyticsService: analyticsService,
      );
    }

    if (widgets.isEmpty) return const SizedBox.shrink();

    final children = <Widget>[];
    for (var i = 0; i < widgets.length; i++) {
      children.add(widgets[i]);
      if (i < widgets.length - 1) {
        children.add(SizedBox(height: spacing));
      }
    }

    Widget result;
    if (scrollable) {
      result = ListView(
        padding: padding,
        shrinkWrap: true,
        children: children,
      );
    } else {
      result = Padding(
        padding: padding,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: children,
        ),
      );
    }

    // Note: Individual widgets are already wrapped with the colorScheme
    // via ResponsiveWidgetWrapper, so we don't need to wrap again here.

    return result;
  }
}
