/// Models for parsing agent JSON responses into widget data.
library;

import 'dart:ui';

import 'package:flutter/material.dart' show Brightness, ColorScheme, EdgeInsets;

/// Layout configuration for responsive widget sizing.
class LayoutConfig {
  final double? width;
  final double? height;
  final double? maxWidth;
  final double? maxHeight;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final bool expand;
  final double? aspectRatio;

  const LayoutConfig({
    this.width,
    this.height,
    this.maxWidth,
    this.maxHeight,
    this.padding,
    this.margin,
    this.expand = true,
    this.aspectRatio,
  });

  factory LayoutConfig.fromJson(Map<String, dynamic> json) {
    return LayoutConfig(
      width: (json['width'] as num?)?.toDouble(),
      height: (json['height'] as num?)?.toDouble(),
      maxWidth: (json['max_width'] as num?)?.toDouble(),
      maxHeight: (json['max_height'] as num?)?.toDouble(),
      padding: _parseEdgeInsets(json['padding']),
      margin: _parseEdgeInsets(json['margin']),
      expand: json['expand'] as bool? ?? true,
      aspectRatio: (json['aspect_ratio'] as num?)?.toDouble(),
    );
  }

  /// Parses JSON edge insets values into Flutter [EdgeInsets].
  ///
  /// Supported formats:
  /// - `num`        — uniform value for all sides, e.g. `16`
  /// - `[num]`      — same as above, e.g. `[16]`
  /// - `[v, h]`     — vertical / horizontal, e.g. `[8, 16]`
  /// - `[t, r, b, l]` — top, right, bottom, left (CSS order)
  ///
  /// **Note:** The 4-value order follows CSS convention: top, right, bottom, left.
  /// This is different from Flutter's `EdgeInsets.fromLTRB(left, top, right, bottom)`.
  static EdgeInsets? _parseEdgeInsets(dynamic value) {
    if (value == null) return null;
    if (value is num) {
      return EdgeInsets.all(value.toDouble());
    }
    if (value is List) {
      if (value.length == 1) return EdgeInsets.all((value[0] as num).toDouble());
      if (value.length == 2) {
        return EdgeInsets.symmetric(
          vertical: (value[0] as num).toDouble(),
          horizontal: (value[1] as num).toDouble(),
        );
      }
      if (value.length == 4) {
        // CSS order: top, right, bottom, left → LTRB(left, top, right, bottom)
        return EdgeInsets.fromLTRB(
          (value[3] as num).toDouble(), // left
          (value[0] as num).toDouble(), // top
          (value[1] as num).toDouble(), // right
          (value[2] as num).toDouble(), // bottom
        );
      }
    }
    return null;
  }

  Map<String, dynamic> toJson() => {
    if (width != null) 'width': width,
    if (height != null) 'height': height,
    if (maxWidth != null) 'max_width': maxWidth,
    if (maxHeight != null) 'max_height': maxHeight,
    'expand': expand,
    if (aspectRatio != null) 'aspect_ratio': aspectRatio,
  };
}

/// Theme override for individual widgets.
class ThemeOverride {
  final Color? backgroundColor;
  final Color? textColor;
  final double? borderRadius;

  const ThemeOverride({this.backgroundColor, this.textColor, this.borderRadius});

  factory ThemeOverride.fromJson(Map<String, dynamic> json) {
    return ThemeOverride(
      backgroundColor: _parseColor(json['bg_color']),
      textColor: _parseColor(json['text_color']),
      borderRadius: (json['border_radius'] as num?)?.toDouble(),
    );
  }

  static Color? _parseColor(dynamic value) {
    if (value == null) return null;
    if (value is String) {
      final hex = value.replaceFirst('#', '');
      if (hex.length == 6) return Color(int.parse('FF$hex', radix: 16));
      if (hex.length == 8) return Color(int.parse(hex, radix: 16));
    }
    return null;
  }
}

/// Parses a color_palette JSON map into a Flutter [ColorScheme].
ColorScheme? parseColorSchemeFromJson(Map<String, dynamic>? json) {
  if (json == null) return null;
  Color? p(String key) => ThemeOverride._parseColor(json[key]);

  final primary = p('primary') ?? const Color(0xFF6200EE);
  final secondary = p('secondary') ?? const Color(0xFF03DAC6);
  final surface = p('surface') ?? const Color(0xFFFFFFFF);
  final background = p('background') ?? const Color(0xFFFFFFFF);
  final error = p('error') ?? const Color(0xFFB00020);
  final onPrimary = p('on_primary') ?? const Color(0xFFFFFFFF);
  final onSecondary = p('on_secondary') ?? const Color(0xFF000000);
  final onSurface = p('on_surface') ?? const Color(0xFF000000);
  final onError = p('on_error') ?? const Color(0xFFFFFFFF);

  // Determine brightness from background luminance
  final brightness =
      background.computeLuminance() > 0.5 ? Brightness.light : Brightness.dark;

  return ColorScheme(
    brightness: brightness,
    primary: primary,
    onPrimary: onPrimary,
    secondary: secondary,
    onSecondary: onSecondary,
    error: error,
    onError: onError,
    surface: surface,
    onSurface: onSurface,
  );
}

/// Common parameters shared by all widget types.
class CommonParams {
  final bool dismissible;
  final int priority;
  final int? ttlSeconds;
  final ThemeOverride? themeOverride;
  final LayoutConfig? layout;

  /// Color scheme parsed from the agent's `color_palette` field.
  final ColorScheme? colorScheme;

  const CommonParams({
    this.dismissible = true,
    this.priority = 0,
    this.ttlSeconds,
    this.themeOverride,
    this.layout,
    this.colorScheme,
  });

  factory CommonParams.fromJson(Map<String, dynamic> json) {
    return CommonParams(
      dismissible: json['dismissible'] as bool? ?? true,
      priority: json['priority'] as int? ?? 0,
      ttlSeconds: json['ttl_seconds'] as int?,
      themeOverride: json['theme_override'] != null
          ? ThemeOverride.fromJson(json['theme_override'] as Map<String, dynamic>)
          : null,
      layout: json['layout'] != null
          ? LayoutConfig.fromJson(json['layout'] as Map<String, dynamic>)
          : null,
      colorScheme: parseColorSchemeFromJson(
        json['color_palette'] as Map<String, dynamic>?,
      ),
    );
  }
}

/// A single widget entry from the agent response.
class WidgetEntry {
  final String id;
  final String type;
  final Map<String, dynamic> params;
  final CommonParams common;

  const WidgetEntry({
    required this.id,
    required this.type,
    required this.params,
    required this.common,
  });

  factory WidgetEntry.fromJson(Map<String, dynamic> json) {
    return WidgetEntry(
      id: json['id'] as String? ?? '',
      type: json['type'] as String,
      params: json['params'] as Map<String, dynamic>? ?? {},
      common: json['common'] != null
          ? CommonParams.fromJson(json['common'] as Map<String, dynamic>)
          : const CommonParams(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'params': params,
  };
}

/// The full agent response containing a list of widgets.
class WidgetResponse {
  final List<WidgetEntry> widgets;

  const WidgetResponse({required this.widgets});

  factory WidgetResponse.fromJson(Map<String, dynamic> json) {
    final list = json['widgets'] as List<dynamic>? ?? [];
    return WidgetResponse(
      widgets: list
          .map((e) => WidgetEntry.fromJson(e as Map<String, dynamic>))
          .toList()
        ..sort((a, b) => b.common.priority.compareTo(a.common.priority)),
    );
  }
}
