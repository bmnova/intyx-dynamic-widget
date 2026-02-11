/// Responsive wrapper that applies layout constraints from JSON config.
library;

import 'package:flutter/material.dart';

import '../models/widget_response.dart';

class ResponsiveWidgetWrapper extends StatelessWidget {
  final LayoutConfig? layout;
  final ThemeOverride? themeOverride;
  final Widget child;

  const ResponsiveWidgetWrapper({
    super.key,
    this.layout,
    this.themeOverride,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    Widget result = child;

    // Apply theme override (background, border radius)
    if (themeOverride != null) {
      result = Container(
        decoration: BoxDecoration(
          color: themeOverride!.backgroundColor,
          borderRadius: themeOverride!.borderRadius != null
              ? BorderRadius.circular(themeOverride!.borderRadius!)
              : null,
        ),
        child: DefaultTextStyle.merge(
          style: TextStyle(color: themeOverride!.textColor),
          child: result,
        ),
      );
    }

    final l = layout;

    if (l == null) {
      // Default: expand to parent width, intrinsic height
      return SizedBox(width: double.infinity, child: result);
    }

    // Apply aspect ratio
    if (l.aspectRatio != null) {
      result = AspectRatio(aspectRatio: l.aspectRatio!, child: result);
    }

    // Apply fixed size or expand
    if (l.width != null || l.height != null) {
      result = SizedBox(width: l.width, height: l.height, child: result);
    } else if (l.expand) {
      result = SizedBox(width: double.infinity, child: result);
    }

    // Apply max constraints
    if (l.maxWidth != null || l.maxHeight != null) {
      result = ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: l.maxWidth ?? double.infinity,
          maxHeight: l.maxHeight ?? double.infinity,
        ),
        child: result,
      );
    }

    // Apply padding
    if (l.padding != null) {
      result = Padding(padding: l.padding!, child: result);
    }

    // Apply margin
    if (l.margin != null) {
      result = Container(margin: l.margin, child: result);
    }

    return result;
  }
}
