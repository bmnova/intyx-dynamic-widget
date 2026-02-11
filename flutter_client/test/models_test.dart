import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:intyx_dynamic_widget/models/widget_response.dart';

void main() {
  group('LayoutConfig', () {
    test('fromJson with all fields', () {
      final config = LayoutConfig.fromJson({
        'width': 300,
        'height': 200,
        'max_width': 500,
        'max_height': 400,
        'expand': false,
        'aspect_ratio': 1.78,
        'padding': [10, 20, 10, 20],
        'margin': 16,
      });

      expect(config.width, 300.0);
      expect(config.height, 200.0);
      expect(config.maxWidth, 500.0);
      expect(config.maxHeight, 400.0);
      expect(config.expand, false);
      expect(config.aspectRatio, 1.78);
      expect(config.padding, isNotNull);
      expect(config.margin, const EdgeInsets.all(16));
    });

    test('fromJson with single padding value', () {
      final config = LayoutConfig.fromJson({'padding': 16});
      expect(config.padding, const EdgeInsets.all(16));
    });

    test('fromJson with two-value padding', () {
      final config = LayoutConfig.fromJson({'padding': [8, 16]});
      expect(config.padding, const EdgeInsets.symmetric(vertical: 8, horizontal: 16));
    });

    test('defaults', () {
      final config = LayoutConfig.fromJson({});
      expect(config.width, isNull);
      expect(config.height, isNull);
      expect(config.expand, true);
      expect(config.aspectRatio, isNull);
    });
  });

  group('ThemeOverride', () {
    test('parse hex color 6 digits', () {
      final theme = ThemeOverride.fromJson({
        'bg_color': '#FF5733',
        'text_color': '#FFFFFF',
        'border_radius': 12.0,
      });
      expect(theme.backgroundColor, isNotNull);
      expect(theme.textColor, const Color(0xFFFFFFFF));
      expect(theme.borderRadius, 12.0);
    });

    test('null values', () {
      final theme = ThemeOverride.fromJson({});
      expect(theme.backgroundColor, isNull);
      expect(theme.textColor, isNull);
      expect(theme.borderRadius, isNull);
    });
  });

  group('CommonParams', () {
    test('fromJson full', () {
      final common = CommonParams.fromJson({
        'dismissible': false,
        'priority': 10,
        'ttl_seconds': 3600,
        'layout': {'width': 300},
        'theme_override': {'bg_color': '#000000'},
      });
      expect(common.dismissible, false);
      expect(common.priority, 10);
      expect(common.ttlSeconds, 3600);
      expect(common.layout, isNotNull);
      expect(common.layout!.width, 300.0);
      expect(common.themeOverride, isNotNull);
    });

    test('defaults', () {
      final common = CommonParams.fromJson({});
      expect(common.dismissible, true);
      expect(common.priority, 0);
      expect(common.ttlSeconds, isNull);
    });
  });

  group('WidgetEntry', () {
    test('fromJson', () {
      final entry = WidgetEntry.fromJson({
        'id': 'w1',
        'type': 'informational',
        'params': {'title': 'Test', 'message': 'Hello'},
        'common': {'priority': 5},
      });

      expect(entry.id, 'w1');
      expect(entry.type, 'informational');
      expect(entry.params['title'], 'Test');
      expect(entry.common.priority, 5);
    });

    test('fromJson with missing common', () {
      final entry = WidgetEntry.fromJson({
        'type': 'informational',
        'params': {'title': 'Test'},
      });
      expect(entry.id, '');
      expect(entry.common.dismissible, true);
      expect(entry.common.priority, 0);
    });
  });

  group('WidgetResponse', () {
    test('fromJson sorts by priority', () {
      final response = WidgetResponse.fromJson({
        'widgets': [
          {'id': 'w1', 'type': 'a', 'params': {}, 'common': {'priority': 1}},
          {'id': 'w2', 'type': 'b', 'params': {}, 'common': {'priority': 10}},
          {'id': 'w3', 'type': 'c', 'params': {}, 'common': {'priority': 5}},
        ],
      });

      expect(response.widgets.length, 3);
      expect(response.widgets[0].id, 'w2'); // highest priority
      expect(response.widgets[1].id, 'w3');
      expect(response.widgets[2].id, 'w1');
    });

    test('empty widgets', () {
      final response = WidgetResponse.fromJson({});
      expect(response.widgets, isEmpty);
    });
  });
}
