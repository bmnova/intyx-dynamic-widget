import 'package:flutter/material.dart';

import '../core/widget_resolver.dart';
import '../models/widget_response.dart';

/// Main container that renders a list of widgets from agent JSON response.
class DynamicWidgetContainer extends StatelessWidget {
  /// Agent response JSON containing widgets array.
  final Map<String, dynamic>? responseJson;

  /// Pre-parsed widget entries (alternative to responseJson).
  final List<WidgetEntry>? entries;

  /// Called when a widget is dismissed.
  final OnWidgetDismiss? onDismiss;

  /// Called when a widget action is triggered.
  final OnWidgetAction? onAction;

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
    this.onDismiss,
    this.onAction,
    this.spacing = 8,
    this.padding = const EdgeInsets.all(16),
    this.scrollable = true,
  }) : assert(
          responseJson != null || entries != null,
          'Either responseJson or entries must be provided',
        );

  @override
  Widget build(BuildContext context) {
    final List<Widget> widgets;

    if (entries != null) {
      widgets = WidgetResolver.resolveEntries(
        entries!,
        onDismiss: onDismiss,
        onAction: onAction,
      );
    } else {
      widgets = WidgetResolver.resolve(
        responseJson!,
        onDismiss: onDismiss,
        onAction: onAction,
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

    if (scrollable) {
      return ListView(
        padding: padding,
        shrinkWrap: true,
        children: children,
      );
    }

    return Padding(
      padding: padding,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: children,
      ),
    );
  }
}
