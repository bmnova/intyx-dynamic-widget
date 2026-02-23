import 'package:flutter/material.dart';

import '../services/widget_service.dart';

/// Wraps a child widget and fires a single `impression` event the first
/// time the widget is laid out on screen.
///
/// The event is sent fire-and-forget; any network error is silently ignored
/// so tracking failures never affect the visible UI.
class ImpressionTracker extends StatefulWidget {
  final String widgetId;
  final String userId;
  final WidgetService service;
  final Widget child;

  const ImpressionTracker({
    super.key,
    required this.widgetId,
    required this.userId,
    required this.service,
    required this.child,
  });

  @override
  State<ImpressionTracker> createState() => _ImpressionTrackerState();
}

class _ImpressionTrackerState extends State<ImpressionTracker> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.service
          .recordInteraction(
            widget.widgetId,
            widget.userId,
            action: 'impression',
          )
          .ignore();
    });
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
